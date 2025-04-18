# Paper Summarizer

A lightweight Vercel Python API for ingesting academic papers (PDF/HTML), summarizing via Vertex AI Gemini Flash, and creating structured pages in Notion.

## Files

- **api/ingest.py**: Main Flask app
- **requirements.txt**: Dependencies
- **vercel.json**: Vercel config

## Setup

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create YOUR_USERNAME/paper-summarizer --public --source=. --remote=origin
   git push -u origin main
   ```

2. **Deploy to Vercel**:
   ```bash
   vercel login
   vercel
   ```

3. **Configure env vars** in Vercel Dashboard:
   - NOTION_TOKEN
   - NOTION_PARENT_ID
   - VERTEX_PROJECT
   - VERTEX_LOCATION (default: us-central1)
   - VERTEX_MODEL (default: models/gemini-1.5-flash-preview-0514)
   - VERTEX_API_KEY

4. **Bookmarklet**:
   ```js
   javascript:(async()=>{
     const notionKey = localStorage.getItem('notionKey')
       || prompt('Enter your Notion API key');
     localStorage.setItem('notionKey', notionKey);
     const res = await fetch('https://<your-vercel-url>/api/ingest', {
       method:'POST',
       headers:{'Content-Type':'application/json'},
       body:JSON.stringify({url:window.location.href, notionKey})
     });
     alert(res.ok ? '✅ Success!' : '❌ '+await res.text());
   })();
   ```

Store keys once and reuse. Share the bookmarklet—anyone will be prompted to enter their own keys.
