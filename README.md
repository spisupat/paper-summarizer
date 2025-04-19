# Web Content Summarizer

A Vercel app that summarizes web content using OpenAI's o4-mini model and copies the summary to your clipboard in markdown format, accessible through a browser bookmarklet.

## Features

- API endpoint to receive HTML content and return a summary
- Browser bookmarklet for easy access from any webpage
- Summarization using OpenAI's o4-mini model
- Automatic clipboard functionality (both server-side and client-side)
- Error handling for various scenarios

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file using the `.env.example` as a template:
   ```
   cp .env.example .env
   ```
4. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
5. Set the environment variable for local development:
   ```
   ENVIRONMENT=development
   ```
6. Run the local development server:
   ```
   python api/index.py
   ```
7. Visit http://localhost:3000 in your browser
8. Drag the "Summarize" bookmarklet to your bookmarks bar

## Usage

1. Navigate to any webpage you want to summarize
2. Click the "Summarize" bookmark in your bookmarks bar
3. Wait for the summary to be generated
4. The summary will automatically be copied to your clipboard in markdown format
5. You can also click the "Preview Summary" button to view the summary before closing

## Testing

Run the tests using:
```
python -m unittest discover tests
```

## Deployment to Vercel

1. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```
2. Deploy to Vercel:
   ```
   vercel
   ```
3. Set up environment variables on Vercel:
   ```
   vercel env add OPENAI_API_KEY
   vercel env add ENVIRONMENT production
   ```

## How It Works

1. The bookmarklet captures the HTML content of the current page
2. It sends the HTML to the API endpoint along with the URL and title
3. The API extracts the text content from the HTML
4. The text is sent to OpenAI's o4-mini model for summarization
5. The markdown summary is returned and copied to the clipboard
6. A success message is displayed to the user

## Limitations

- The server-side clipboard functionality only works in local development, not in a serverless environment like Vercel
- The client-side clipboard functionality requires user interaction in some browsers
- The summary quality depends on the content and quality of the webpage

## License

MIT 