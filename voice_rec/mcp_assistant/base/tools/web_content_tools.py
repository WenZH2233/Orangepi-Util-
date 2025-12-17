import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('Tools.WebContent')

def read_webpage(url: str) -> str:
    """
    Read the text content of a webpage.
    
    Args:
        url: The URL of the webpage to read.
    
    Returns:
        The text content of the webpage (truncated to 5000 characters).
    """
    try:
        logger.info(f"Fetching URL: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Use response.content to let BeautifulSoup detect encoding from meta tags or byte content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script, style, nav, footer, header elements to clean up
        for element in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
            element.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit length to avoid context overflow
        max_length = 5000
        if len(text) > max_length:
            text = text[:max_length] + f"\n\n[Content truncated. Original length: {len(text)} characters]"
            
        return text
        
    except Exception as e:
        logger.error(f"Error reading webpage: {e}")
        return f"Error reading webpage: {str(e)}"
