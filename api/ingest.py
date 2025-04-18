import os
import logging
from flask import Flask, request, jsonify
import requests
import json
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variables\NOTION_PARENT_ID = os.environ.get("NOTION_PARENT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "o4-mini")

# Initialize OpenAI API key
openai.api_key = OPENAI_API_KEY


def fetch_text(url: str) -> str:
    logger.info(f"Fetching URL: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    if url.lower().endswith(".pdf"):
        doc = fitz.open(stream=resp.content, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
    else:
        text = BeautifulSoup(resp.text, "html.parser").get_text()
    logger.info(f"Fetched text length: {len(text)} characters")
    return text


def summarize(text: str) -> dict:
    logger.info("Starting summarization with OpenAI o4-mini")
    prompt = (
        "Extract the following fields from this academic paper: "
        "title (string), authors (array), abstract (string), summary (string), methodology (string), "
        "conclusion (string), tags (array of keywords). "
        "Return ONLY a valid JSON object with these keys and no extra text.\n\n" + text
    )
    logger.debug(f"Prompt length: {len(prompt)}")
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    content = response.choices[0].message.content
    logger.info("Received summary from OpenAI")
    try:
        summary = json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("JSON decode error", exc_info=e)
        raise
    return summary


def make_blocks(summary: dict) -> list:
    logger.info("Constructing Notion blocks")
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
    logger.info("Received /api/ingest request")
    data = request.get_json() or {}
    url = data.get("url")
    notion_key = data.get("notionKey") or os.environ.get("NOTION_TOKEN")
    parent_id = data.get("notionParentId") or NOTION_PARENT_ID
    logger.info(f"Parameters: url={url}, parent_id={parent_id}")

    if not url or not notion_key or not parent_id:
        error_msg = "Missing URL, notionKey, or parentId"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 400

    try:
        text = fetch_text(url)
        summary = summarize(text)

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
        logger.info("Posting to Notion")
        res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
        logger.info(f"Notion response status: {res.status_code}")

        return jsonify({"status": "ok", "title": summary.get("title") or "Untitled"})

    except Exception as e:
        logger.exception("Error in /api/ingest")
        return jsonify({"error": str(e)}), 500


@app.route("/api/pages", methods=["GET"])
def list_pages():
    logger.info("Received /api/pages request")
    token = request.args.get("notionKey") or os.environ.get("NOTION_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}
    try:
        response = requests.post("https://api.notion.com/v1/search", headers=headers, json={"page_size": 20})
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
        logger.info(f"Found {len(pages)} pages")
        return jsonify(pages)
    except Exception as e:
        logger.exception("Error in /api/pages")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
