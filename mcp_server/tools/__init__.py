"""Tool registry - automatically discovers and loads all tools"""

import importlib
import logging
from typing import Dict, List, Callable, Any

logger = logging.getLogger(__name__)

# Tool modules to load
TOOL_MODULES = [
    'mcp_server.tools.file_tools',
    'mcp_server.tools.code_tools',
    'mcp_server.tools.web_tools',
]


class ToolRegistry:
    """Registry for all available tools"""
    
    def __init__(self):
        self.tools: Dict[str, Dict] = {}  # tool_name -> metadata
        self.handlers: Dict[str, Callable] = {}  # tool_name -> function
        self._load_tools()
    
    def _load_tools(self):
        """Automatically load all tools from modules"""
        for module_name in TOOL_MODULES:
            try:
                module = importlib.import_module(module_name)
                
                # Get tool metadata
                if hasattr(module, 'TOOLS'):
                    for tool_def in module.TOOLS:
                        tool_name = tool_def['name']
                        self.tools[tool_name] = tool_def
                        
                        # Get handler function
                        if hasattr(module, tool_name):
                            self.handlers[tool_name] = getattr(module, tool_name)
                            logger.info(f"Loaded tool: {tool_name}")
                        else:
                            logger.warning(f"Tool {tool_name} has no handler function")
            
            except Exception as e:
                logger.error(f"Error loading tool module {module_name}: {e}")
    
    def get_tool_definitions(self) -> List[Dict]:
        """Get all tool definitions in Ollama format"""
        return [
            {
                'type': 'function',
                'function': tool_def
            }
            for tool_def in self.tools.values()
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool by name"""
        if tool_name not in self.handlers:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        handler = self.handlers[tool_name]
        
        try:
            result = handler(**arguments)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    def list_tool_names(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())


# Global registry instance
_registry = None

def get_registry() -> ToolRegistry:
    """Get the global tool registry"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry