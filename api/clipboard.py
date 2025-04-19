import pyperclip

def copy_to_clipboard(text):
    """
    Copy the given text to the clipboard.
    
    Args:
        text (str): The text to copy to the clipboard
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {str(e)}")
        return False 