"""File operation tools for MCP server"""

from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Tool metadata for automatic registration
TOOLS = [
    {
        'name': 'file_read',
        'description': 'Read contents of a file',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                    'description': 'Path to the file to read'
                }
            },
            'required': ['path']
        }
    },
    {
        'name': 'file_write',
        'description': 'Write content to a file',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                    'description': 'Path to the file to write'
                },
                'content': {
                    'type': 'string',
                    'description': 'Content to write to the file'
                }
            },
            'required': ['path', 'content']
        }
    },
    {
        'name': 'list_directory',
        'description': 'List contents of a directory',
        'parameters': {
            'type': 'object',
            'properties': {
                'path': {
                    'type': 'string',
                    'description': 'Path to the directory'
                }
            },
            'required': ['path']
        }
    }
]


def file_read(path: str) -> str:
    """Read contents of a file"""
    try:
        file_path = Path(path)
        content = file_path.read_text(encoding='utf-8')
        logger.info(f"Read file: {path}")
        return content
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        raise


def file_write(path: str, content: str) -> str:
    """Write content to a file"""
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        logger.info(f"Wrote file: {path}")
        return f"Successfully wrote to {path}"
    except Exception as e:
        logger.error(f"Error writing file {path}: {e}")
        raise


def list_directory(path: str) -> str:
    """List contents of a directory"""
    try:
        dir_path = Path(path)
        items = [item.name for item in dir_path.iterdir()]
        logger.info(f"Listed directory: {path}")
        return "\n".join(items)
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        raise