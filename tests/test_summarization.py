import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.summarizer import extract_content, create_summary

class TestSummarization(unittest.TestCase):

    def test_extract_content(self):
        """Test that extract_content extracts text from HTML"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Title</title>
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a paragraph.</p>
            <script>console.log('This should be ignored');</script>
            <style>.ignored { display: none; }</style>
        </body>
        </html>
        """
        
        content = extract_content(html)
        
        # Check that the title is extracted
        self.assertIn("Main Heading", content)
        
        # Check that paragraph content is extracted
        self.assertIn("This is a paragraph", content)
        
        # Check that script and style content is ignored
        self.assertNotIn("This should be ignored", content)
        self.assertNotIn(".ignored", content)
        
    @patch('api.summarizer.openai.OpenAI')
    def test_create_summary(self, mock_openai):
        """Test that create_summary calls OpenAI API and returns formatted markdown"""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_chat_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_chat_completion
        
        # Mock the response content
        mock_chat_completion.choices = [MagicMock()]
        mock_chat_completion.choices[0].message.content = "This is a test summary"
        
        # Call the function
        result = create_summary("Test Title", "https://example.com", "This is test content")
        
        # Verify OpenAI was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        
        # Check model parameter
        self.assertEqual(call_args["model"], "o4-mini")
        
        # Check messages structure
        messages = call_args["messages"]
        self.assertTrue(any("summarize" in str(msg).lower() for msg in messages))
        self.assertTrue(any("Test Title" in str(msg) for msg in messages))
        self.assertTrue(any("https://example.com" in str(msg) for msg in messages))
        
        # Check that the result is a markdown string with the expected format
        self.assertEqual(result, "This is a test summary")

if __name__ == '__main__':
    unittest.main() 