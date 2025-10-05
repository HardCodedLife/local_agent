"""Agent Controller - Pure orchestration logic without UI"""

import logging
from typing import Dict, List, Any, Optional
import ollama

from agent_controller.model_router import ModelRouter
from agent_controller.mcp_client import MCPClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalAgent:
    """Local AI agent with tool support - Pure logic, no UI"""
    
    def __init__(self, default_model: str = "llama3.1:8b", coder_model: str = "qwen2.5-coder:7b"):
        self.model_router = ModelRouter(default_model, coder_model)
        self.mcp_client = MCPClient()
        self.current_model = default_model
        self.conversation_history: List[Any] = []
        self.tools = self._get_tool_definitions()
        logger.info("LocalAgent initialized")
    
    def _get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions for Ollama"""
        return [
            {
                'type': 'function',
                'function': {
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
                }
            },
            {
                'type': 'function',
                'function': {
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
                }
            },
            {
                'type': 'function',
                'function': {
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
            }
        ]
    
    def chat(self, user_message: str, model_override: Optional[str] = None) -> str:
        """
        Send a message to the agent and get a response
        
        Args:
            user_message: The user's message
            model_override: Optional model to use instead of auto-selection
            
        Returns:
            The agent's response as a string
        """
        # Select model
        if model_override:
            self.current_model = model_override
        else:
            self.current_model = self.model_router.select_model(user_message)
        
        logger.info(f"Using model: {self.current_model}")
        
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        try:
            # Call Ollama with tools
            response = ollama.chat(
                model=self.current_model,
                messages=self.conversation_history,
                tools=self.tools
            )
            
            assistant_message = response['message']
            self.conversation_history.append(assistant_message)
            
            if assistant_message.get('tool_calls'):
                logger.info(f"Model requested {len(assistant_message['tool_calls'])} tool calls")
                
                # Execute each tool call via MCP client
                for tool_call in assistant_message['tool_calls']:
                    function_name = tool_call['function']['name']
                    function_args = tool_call['function']['arguments']
                    
                    # Execute tool via MCP client
                    tool_result = self.mcp_client.call_tool(function_name, function_args)
                    
                    # Add tool result to conversation
                    self.conversation_history.append({
                        'role': 'tool',
                        'content': tool_result
                    })
                
                # Get final response with tool results
                final_response = ollama.chat(
                    model=self.current_model,
                    messages=self.conversation_history
                )
                
                final_message = final_response['message']
                self.conversation_history.append(final_message)
                
                return final_message['content']
            
            else:
                return assistant_message['content']
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.current_model = self.model_router.default_model
        logger.info("Conversation history reset")
    
    def get_history(self) -> List[Dict]:
        """Get conversation history as serializable dicts"""
        history_serializable = []
        for msg in self.conversation_history:
            if hasattr(msg, 'model_dump'):
                history_serializable.append(msg.model_dump())
            else:
                history_serializable.append(msg)
        return history_serializable
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            'default_model': self.model_router.default_model,
            'coder_model': self.model_router.coder_model,
            'current_model': self.current_model,
            'available_tools': self.mcp_client.list_tools(),
            'conversation_length': len(self.conversation_history)
        }