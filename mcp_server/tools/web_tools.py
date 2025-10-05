"""Web-related tools for MCP server"""

import logging
import requests
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Tool metadata
TOOLS = [
    {
        'name': 'web_search',
        'description': 'Search the web for current information using Brave Search. Use this to find facts, news, documentation, or any information not in your knowledge base.',
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': 'Search query - be specific for better results'
                },
                'max_results': {
                    'type': 'integer',
                    'description': 'Maximum number of results to return (default: 5)',
                    'default': 5
                }
            },
            'required': ['query']
        }
    }
]


def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using Brave Search API
    
    Args:
        query: Search query
        max_results: Maximum number of results (default: 5)
        
    Returns:
        Formatted search results
    """
    logger.info(f"Web search via Brave: {query}")
    
    # Get API key from environment variable
    api_key = os.getenv("BRAVE_API_KEY")
    
    if not api_key:
        error_msg = "BRAVE_API_KEY not found in environment variables"
        logger.error(error_msg)
        return f"Error: {error_msg}\nPlease set BRAVE_API_KEY in your .env file"
    
    try:
        # Brave Search API endpoint
        url = "https://api.search.brave.com/res/v1/web/search"
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
        
        params = {
            "q": query,
            "count": max_results,
            "text_decorations": False,  # Disable HTML in snippets
            "search_lang": "en"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract results
        web_results = data.get("web", {}).get("results", [])
        
        if not web_results:
            return f"No results found for '{query}'."
        
        # Format results
        output = [f"Search results for '{query}':\n"]
        
        for i, result in enumerate(web_results[:max_results], 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            description = result.get("description", "No description")
            
            output.append(f"{i}. {title}")
            output.append(f"   URL: {url}")
            output.append(f"   {description}\n")
        
        logger.info(f"Found {len(web_results)} results")
        return "\n".join(output)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request error: {e}")
        return f"Search request failed: {str(e)}"
    
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return f"Search error: {str(e)}"