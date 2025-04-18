import os
from flask import Flask, request, jsonify
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import openai

# Initialize Flask and OpenAI
app = Flask(__name__)
openai.api_key = os.environ.get('OPENAI_API_KEY')
MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4.1')


def fetch_text(url: str) -> str:
    """Download PDF or HTML and extract plain text."""
    resp = requests.get(url)
    resp.raise_for_status()
    if url.lower().endswith('.pdf'):
        doc = fitz.open(stream=resp.content, filetype='pdf')
        return "\n".join(p.get_text() for p in doc)
    # HTML page
    return BeautifulSoup(resp.text, 'html.parser').get_text()


@app.route('/api/ingest', methods=['POST'])
def ingest():
    data = request.get_json() or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'Missing url'}), 400

    # Fetch and summarize
    text = fetch_text(url)
    prompt = f"""
Summarize this academic paper into a Markdown snippet with sections:

# Motivation
...

# Key contributions
...

# Methods
...

# Results
...

# Limitations
...

Paper content:
```
{text}
```
"""
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}],
    )
    md = response.choices[0].message.content

    return jsonify({'status': 'ok', 'markdown': md})


if __name__ == '__main__':
    app.run(debug=True)
