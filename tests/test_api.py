import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.index import app

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_route(self):
        """Test the home route returns 200 status code"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_summarize_endpoint_exists(self):
        """Test that the summarize endpoint exists and accepts POST requests"""
        with patch('api.index.extract_content', return_value="Content"):
            with patch('api.index.create_summary', return_value="Summary"):
                with patch('api.index.copy_to_clipboard', return_value=True):
                    response = self.app.post('/api/summarize', 
                                        data=json.dumps({"html": "<html></html>", "url": "http://example.com", "title": "Example"}),
                                        content_type='application/json')
                    self.assertNotEqual(response.status_code, 404)
        
    def test_summarize_endpoint_requires_html(self):
        """Test that the summarize endpoint requires the html parameter"""
        response = self.app.post('/api/summarize', 
                               data=json.dumps({"url": "http://example.com", "title": "Example"}),
                               content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        
    @patch('api.index.extract_content')
    @patch('api.index.create_summary')
    @patch('api.index.copy_to_clipboard')
    @patch('api.index.os.environ.get')
    def test_summarize_endpoint_success(self, mock_env, mock_copy, mock_create_summary, mock_extract):
        """Test that the summarize endpoint successfully processes HTML and returns a summary"""
        # Mock environment to enable clipboard functionality
        mock_env.return_value = 'development'
        
        # Mock the extract_content and create_summary functions
        mock_extract.return_value = "Extracted content"
        mock_create_summary.return_value = "# Example Summary\n\nThis is a summary of the content."
        mock_copy.return_value = True
        
        response = self.app.post('/api/summarize', 
                               data=json.dumps({
                                   "html": "<html><body><h1>Test</h1><p>Content</p></body></html>",
                                   "url": "http://example.com",
                                   "title": "Example"
                               }),
                               content_type='application/json')
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('summary', data)
        self.assertEqual(data['summary'], "# Example Summary\n\nThis is a summary of the content.")
        self.assertIn('clipboard_copied', data)
        self.assertTrue(data['clipboard_copied'])
        
        # Verify that extract_content was called with the HTML
        mock_extract.assert_called_once()
        
        # Verify that create_summary was called with the correct arguments
        mock_create_summary.assert_called_once_with("Example", "http://example.com", "Extracted content")
        
        # Verify that copy_to_clipboard was called with the summary
        mock_copy.assert_called_once_with("# Example Summary\n\nThis is a summary of the content.")
        
    @patch('api.index.extract_content')
    @patch('api.index.create_summary')
    @patch('api.index.copy_to_clipboard')
    @patch('api.index.os.environ.get')
    def test_summarize_endpoint_production(self, mock_env, mock_copy, mock_create_summary, mock_extract):
        """Test that clipboard is not used in production environment"""
        # Mock environment to disable clipboard functionality
        mock_env.return_value = 'production'
        
        # Mock the extract_content and create_summary functions
        mock_extract.return_value = "Extracted content"
        mock_create_summary.return_value = "# Example Summary\n\nThis is a summary of the content."
        
        response = self.app.post('/api/summarize', 
                               data=json.dumps({
                                   "html": "<html><body><h1>Test</h1><p>Content</p></body></html>",
                                   "url": "http://example.com",
                                   "title": "Example"
                               }),
                               content_type='application/json')
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('clipboard_copied', data)
        self.assertFalse(data['clipboard_copied'])
        
        # Verify that copy_to_clipboard was not called
        mock_copy.assert_not_called()
        
    @patch('api.index.extract_content')
    @patch('api.index.create_summary')
    def test_summarize_endpoint_api_key_error(self, mock_create_summary, mock_extract):
        """Test that the summarize endpoint handles API key errors"""
        # Mock the extract_content function
        mock_extract.return_value = "Extracted content"
        
        # Mock the create_summary function to raise a ValueError
        mock_create_summary.side_effect = ValueError("OpenAI API key is not set")
        
        response = self.app.post('/api/summarize', 
                               data=json.dumps({
                                   "html": "<html><body><h1>Test</h1><p>Content</p></body></html>",
                                   "url": "http://example.com",
                                   "title": "Example"
                               }),
                               content_type='application/json')
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', data)
        self.assertIn('OpenAI API key is not set', data['error'])
        
    @patch('api.index.extract_content')
    @patch('api.index.create_summary')
    def test_summarize_endpoint_other_error(self, mock_create_summary, mock_extract):
        """Test that the summarize endpoint handles other errors"""
        # Mock the extract_content function
        mock_extract.return_value = "Extracted content"
        
        # Mock the create_summary function to raise an Exception
        mock_create_summary.side_effect = Exception("General error")
        
        response = self.app.post('/api/summarize', 
                               data=json.dumps({
                                   "html": "<html><body><h1>Test</h1><p>Content</p></body></html>",
                                   "url": "http://example.com",
                                   "title": "Example"
                               }),
                               content_type='application/json')
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 206)  # Partial content
        self.assertIn('error', data)
        self.assertIn('Error generating summary', data['error'])
        self.assertIn('summary', data)
        self.assertIn('Example', data['summary'])
        self.assertIn('Error generating summary', data['summary'])

if __name__ == '__main__':
    unittest.main()