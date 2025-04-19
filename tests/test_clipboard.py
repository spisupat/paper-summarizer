import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.clipboard import copy_to_clipboard

class TestClipboard(unittest.TestCase):

    @patch('api.clipboard.pyperclip.copy')
    def test_copy_to_clipboard(self, mock_copy):
        """Test that copy_to_clipboard calls pyperclip.copy with the given text"""
        # Call the function with some markdown
        markdown = "# Test Heading\n\nThis is a test summary."
        result = copy_to_clipboard(markdown)
        
        # Verify pyperclip.copy was called with the correct argument
        mock_copy.assert_called_once_with(markdown)
        
        # Verify the function returns success message
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main() 