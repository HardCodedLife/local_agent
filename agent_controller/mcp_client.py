"""MCP Client - Connects to MCP server and executes tools"""

import logging
from typing import Dict, Any, List
import ollama

# Import tool registry
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from mcp_server.tools import get_registry
from shared.config import CODER_MODEL

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for connecting to MCP server
    
    Phase 1: Direct tool execution using registry
    Phase 2: Will connect to actual MCP server via stdio/HTTP
    """
    
    def __init__(self, coder_model: str = CODER_MODEL):
        self.connected = False
        self.coder_model = coder_model
        self.registry = get_registry()  # Get tool registry
        logger.info(f"MCPClient initialized with {len(self.registry.list_tool_names())} tools")
    
    def connect(self):
        """Connect to MCP server (placeholder for Phase 2)"""
        self.connected = True
        logger.info("MCPClient connected (simulated)")
    
    def disconnect(self):
        """Disconnect from MCP server"""
        self.connected = False
        logger.info("MCPClient disconnected")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool via the registry
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        try:
            # Special handling for code_assistant
            if tool_name == "code_assistant":
                return self._call_code_assistant(
                    task=arguments.get("task", ""),
                    language=arguments.get("language", "python"),
                    context=arguments.get("context", "")
                )
            
            # Call through registry
            result = self.registry.call_tool(tool_name, arguments)
            return result
        
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            return f"Error: {str(e)}"
    
    def _call_code_assistant(self, task: str, language: str, context: str) -> str:
        """
        Call the specialized coding model
        
        Args:
            task: Description of the coding task
            language: Programming language
            context: Additional context
            
        Returns:
            Code or explanation from the coder model
        """
        logger.info(f"Calling code assistant for task: {task}")
        
        # Build prompt for coder model
        prompt = f"Language: {language}\n"
        if context:
            prompt += f"Context: {context}\n"
        prompt += f"\nTask: {task}\n\nProvide clear, well-commented code:"
        
        try:
            response = ollama.chat(
                model=self.coder_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            
            coder_response = response['message']['content']
            logger.info(f"Code assistant completed task")
            return coder_response
        
        except Exception as e:
            logger.error(f"Error calling code assistant: {e}")
            return f"Code assistant error: {str(e)}"
    
    def list_tools(self) -> List[str]:
        """List available tools from registry"""
        return self.registry.list_tool_names()
    
    def get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions in Ollama format"""
        return self.registry.get_tool_definitions()