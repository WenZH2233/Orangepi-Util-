import logging
from duckduckgo_search import DDGS

logger = logging.getLogger('Tools.WebSearch')

def web_search(query: str, max_results: int = 5) -> str:
    """
    Perform a web search using DuckDuckGo and return the results.
    
    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 5).
    
    Returns:
        A formatted string containing the search results (title, link, and snippet).
    """
    try:
        logger.info(f"Searching for: {query}")
        results = []
        with DDGS() as ddgs:
            # ddgs.text returns an iterator
            for r in ddgs.text(query, max_results=max_results):
                results.append(r)
        
        if not results:
            return "No results found."
            
        formatted_results = []
        for i, res in enumerate(results, 1):
            title = res.get('title', 'No Title')
            link = res.get('href', '#')
            body = res.get('body', 'No description available.')
            formatted_results.append(f"{i}. {title}\n   Link: {link}\n   Snippet: {body}\n")
            
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return f"Error performing web search: {str(e)}"
