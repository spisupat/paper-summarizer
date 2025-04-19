from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from .summarizer import extract_content, create_summary
from .clipboard import copy_to_clipboard

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    
    # Validate required fields
    if not data or 'html' not in data:
        return jsonify({"error": "HTML content is required"}), 400
        
    html_content = data.get('html')
    url = data.get('url', '')
    title = data.get('title', '')
    
    try:
        # Extract text content from HTML
        extracted_content = extract_content(html_content)
        
        # Create summary using OpenAI
        summary = create_summary(title, url, extracted_content)
        
        # Copy to clipboard (this won't work in a serverless environment,
        # but we'll include the code for local development)
        clipboard_success = False
        if os.environ.get('ENVIRONMENT') != 'production':
            clipboard_success = copy_to_clipboard(summary)
        
        # Return the summary
        return jsonify({
            "summary": summary,
            "clipboard_copied": clipboard_success
        })
    except ValueError as e:
        # Handle API key errors - return 500 status code
        error_message = str(e)
        return jsonify({"error": error_message}), 500
    except Exception as e:
        # Handle other errors - use a custom error message
        error_message = f"Error generating summary: General error occurred"
        return jsonify({
            "error": error_message,
            "summary": f"# {title}\n\n**Error generating summary:** General error occurred"
        }), 206  # Partial content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000))) 