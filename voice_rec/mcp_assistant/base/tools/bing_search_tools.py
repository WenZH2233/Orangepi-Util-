import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('Tools.BingSearch')

def web_search(query: str, max_results: int = 5) -> str:
    """
    Perform a web search using Bing and return the results. This tool should be used in combination with **read_webpage**.
    
    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 5).
    
    Returns:
        A formatted string containing the search results.
    """
    try:
        logger.info(f"Searching Bing for: {query}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # Use global Bing to avoid some regional redirection issues, or just standard bing
        url = "https://www.bing.com/search"
        params = {"q": query}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Bing search results are usually in <li class="b_algo">
        # We iterate and extract
        count = 0
        for item in soup.find_all('li', class_='b_algo'):
            if count >= max_results:
                break
                
            title_tag = item.find('h2')
            link_tag = item.find('a')
            
            # Snippet can be in different places depending on the result type
            # Common one is <div class="b_caption"><p>
            caption_div = item.find('div', class_='b_caption')
            snippet = "No description."
            if caption_div:
                p_tag = caption_div.find('p')
                if p_tag:
                    snippet = p_tag.get_text()
            
            if title_tag and link_tag:
                title = title_tag.get_text()
                link = link_tag.get('href')
                
                results.append(f"{count+1}. {title}\n   Link: {link}\n   Snippet: {snippet}\n")
                count += 1
                
        if not results:
            return "No results found on Bing."
            
        return "\n".join(results)
        
    except Exception as e:
        logger.error(f"Bing search error: {e}")
        return f"Error performing Bing search: {str(e)}"
