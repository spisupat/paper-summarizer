from flask import Flask, request, jsonify
import os
import requests
import json
import fitz  # PyMuPDF
from bs4 import BeautifulSoup

app = Flask(__name__)

# Default env var fallback (optional)
NOTION_PARENT_ID = os.environ.get("NOTION_PARENT_ID")


def fetch_text(url: str) -> str:
    resp = requests.get(url)
    if url.lower().endswith(".pdf"):
        doc = fitz.open(stream=resp.content, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    return BeautifulSoup(resp.text, "html.parser").get_text()


def summarize(text: str) -> dict:
    # Vertex AI environment
    project = os.environ.get("VERTEX_PROJECT")
    location = os.environ.get("VERTEX_LOCATION", "us-central1")
    model = os.environ.get("VERTEX_MODEL", "models/gemini-1.5-flash-preview-0514")
    api_key = os.environ.get("VERTEX_API_KEY")

    endpoint = (
        f"https://{location}-aiplatform.googleapis.com"
        f"/v1/projects/{project}/locations/{location}"
        f"/publishers/google/models/{model}:streamGenerateContent"
    )
    # Stronger prompt for strict JSON output
    prompt = (
        "Extract the following fields from this academic paper:"
        " title (string), authors (array), abstract (string), summary (string), methodology (string),"
        " conclusion (string), tags (array of keywords)."
        " Return ONLY a valid JSON object with these keys and no extra text.\n\n" + text
    )
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}
    resp = requests.post(endpoint, headers=headers, json=payload, stream=True)
    for line in resp.iter_lines():
        if line.startswith(b"data: "):
            chunk = json.loads(line.replace(b"data: ", b""))
            return json.loads(chunk["candidates"][0]["content"]["parts"][0]["text"])
    return {}


def make_blocks(summary: dict) -> list:
    blocks = []
    for key in ["authors", "abstract", "summary", "methodology", "conclusion", "tags"]:
        content = summary.get(key)
        if isinstance(content, list):
            content = ", ".join(content)
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": key.capitalize()}}]}
        })
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": content or 'N/A'}}]}
        })
    return blocks


@app.route("/api/ingest", methods=["POST"])
def ingest():
    data = request.get_json() or {}
    url = data.get("url")
    notion_key = data.get("notionKey") or os.environ.get("NOTION_TOKEN")
    parent_id = data.get("notionParentId") or os.environ.get("NOTION_PARENT_ID")

    if not url or not notion_key or not parent_id:
        return jsonify({"error": "Missing URL, notionKey, or parentId"}), 400

    try:
        text = fetch_text(url)
        summary = summarize(text)

        # Push to Notion
        headers = {
            "Authorization": f"Bearer {notion_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        payload = {
            "parent": {"page_id": parent_id},
            "properties": {
                "Title": {"title": [{"text": {"content": summary.get("title") or "Untitled"}}]}
            },
            "children": make_blocks(summary)
        }
        requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)

        # Return with safe title fallback
        return jsonify({"status": "ok", "title": summary.get("title") or "Untitled"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pages", methods=["GET"])
def list_pages():
    token = request.args.get("notionKey") or os.environ.get("NOTION_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.post(
        "https://api.notion.com/v1/search",
        headers=headers,
        json={"page_size": 20}
    )
    results = response.json().get("results", [])
    pages = []
    for page in results:
        if page.get("object") == "page":
            title = "(Untitled)"
            props = page.get("properties", {})
            for val in props.values():
                if val.get("type") == "title" and val["title"]:
                    title = val["title"][0]["plain_text"]
            pages.append({"id": page["id"].replace("-", ""), "title": title})
    return jsonify(pages)


if __name__ == "__main__":
    app.run()
