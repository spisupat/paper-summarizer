import os
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_content(html):
    """
    Extract relevant text content from HTML.
    
    Args:
        html (str): HTML content of the webpage
        
    Returns:
        str: Extracted text content
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    # Get text content
    text = soup.get_text(separator='\n', strip=True)
    
    return text

def create_summary(title, url, content):
    """
    Create a summary of the webpage content using OpenAI's o4-mini model.
    
    Args:
        title (str): Title of the webpage
        url (str): URL of the webpage
        content (str): Extracted text content of the webpage
        
    Returns:
        str: Markdown-formatted summary
    """
    # Check if API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
    
    # Initialize the OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    # Prepare the prompt
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes web content into concise markdown summaries. Your summaries are clear, well-organized, and capture the key points from the source material."},
        {"role": "user", "content": f"Please summarize the following web content from '{title}' ({url}).\n\nContent:\n{content}\n\nCreate a concise, well-structured markdown summary with appropriate headings and bullet points where needed. Focus on the most important information."}
    ]
    
    # Call the OpenAI API
    response = client.chat.completions.create(
        model="o4-mini",
        messages=messages,
        temperature=0.5,
        max_completion_tokens=1000
    )
    
    # Get the summary from the response
    summary = response.choices[0].message.content
    
    return summary 