"""File operation tools for MCP server"""

from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

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