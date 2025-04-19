import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.index import app
from api.summarizer import extract_content, create_summary
from api.clipboard import copy_to_clipboard

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Set up test data
        self.test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Test Page</h1>
            <p>This is a test page with some content that needs to be summarized.</p>
            <p>It contains multiple paragraphs with information about testing.</p>
            <script>console.log('This should be ignored');</script>
        </body>
        </html>
        """
        self.test_url = "https://example.com/test"
        self.test_title = "Test Page"
        
    @patch('api.summarizer.openai.OpenAI')
    @patch('api.clipboard.pyperclip.copy')
    @patch('api.index.os.environ.get')
    def test_full_integration(self, mock_env, mock_clipboard, mock_openai):
        """Test the full integration of extract_content, create_summary, and copy_to_clipboard"""
        # Mock environment to enable clipboard functionality
        mock_env.return_value = 'development'
        
        # Mock OpenAI API
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_chat_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_chat_completion
        
        # Mock the response content
        mock_chat_completion.choices = [MagicMock()]
        mock_chat_completion.choices[0].message.content = "# Test Page Summary\n\nThis is a test summary of the page content."
        
        # Call the API endpoint
        response = self.app.post('/api/summarize', 
                               json={
                                   "html": self.test_html,
                                   "url": self.test_url,
                                   "title": self.test_title
                               })
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('summary', response_data)
        self.assertIn('clipboard_copied', response_data)
        self.assertTrue(response_data['clipboard_copied'])
        
        # Verify extracted content doesn't contain script content
        extracted_content = extract_content(self.test_html)
        self.assertIn("Test Page", extracted_content)
        self.assertIn("some content that needs to be summarized", extracted_content)
        self.assertNotIn("This should be ignored", extracted_content)
        
        # Verify that OpenAI API was called with the extracted content
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify clipboard was called with the summary
        mock_clipboard.assert_called_once_with("# Test Page Summary\n\nThis is a test summary of the page content.")

if __name__ == '__main__':
    unittest.main() 