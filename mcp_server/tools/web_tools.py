"""Web-related tools for MCP server"""

import logging

logger = logging.getLogger(__name__)

# Tool metadata
TOOLS = [
    {
        'name': 'web_search',
        'description': 'Search the web for information',
        'parameters': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': 'Search query'
                }
            },
            'required': ['query']
        }
    }
]


def web_search(query: str) -> str:
    """Search the web - placeholder for Phase 2"""
    logger.warning("web_search not yet implemented")
    return f"Web search for '{query}' - Not implemented yet"