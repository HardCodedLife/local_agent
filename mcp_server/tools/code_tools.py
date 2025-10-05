"""Code-related tools for MCP server"""

import logging

logger = logging.getLogger(__name__)

# Tool metadata
TOOLS = [
    {
        'name': 'code_assistant',
        'description': 'Delegate coding tasks to a specialized coding model. Use this for writing, debugging, refactoring, or explaining code.',
        'parameters': {
            'type': 'object',
            'properties': {
                'task': {
                    'type': 'string',
                    'description': 'Clear description of the coding task'
                },
                'language': {
                    'type': 'string',
                    'description': 'Programming language (e.g., python, javascript, java)',
                    'default': 'python'
                },
                'context': {
                    'type': 'string',
                    'description': 'Additional context or requirements for the code',
                    'default': ''
                }
            },
            'required': ['task']
        }
    }
]


def code_assistant(task: str, language: str = "python", context: str = "") -> str:
    """
    Delegate to specialized coding model
    
    Note: The actual LLM call happens in MCPClient, this is just the interface
    """
    # This will be implemented by MCPClient
    return f"CODE_ASSISTANT_CALL|{task}|{language}|{context}"