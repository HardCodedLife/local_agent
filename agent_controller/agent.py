"""Agent Controller - Pure orchestration logic without UI"""

import logging
from pathlib import Path
import ollama
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalAgent:
    """Local AI agent with tool support - Pure logic, no UI"""
    
    def __init__(self, orchestrator_model: str = "granite4:micro-h", coder_model: str = "deepcoder:1.5b"):
        self.orchestrator_model = orchestrator_model
        self.coder_model = coder_model
        self.conversation_history: List[Any] = []
        self.tools = self._get_tool_definitions()
        logger.info(f"LocalAgent initialized - Orchestrator: {orchestrator_model}, Coder: {coder_model}")
    
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
            },
            {
                'type': 'function',
                'function': {
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
            }
        ]
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """Execute a tool call"""
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        try:
            if tool_name == "file_read":
                path = Path(arguments["path"])
                content = path.read_text(encoding='utf-8')
                return content
            
            elif tool_name == "file_write":
                path = Path(arguments["path"])
                content = arguments["content"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')
                return f"Successfully wrote to {path}"
            
            elif tool_name == "list_directory":
                path = Path(arguments["path"])
                items = [item.name for item in path.iterdir()]
                return "\n".join(items)
            
            elif tool_name == "code_assistant":
                # Delegate to specialized coder model
                return self._call_code_assistant(
                    task=arguments["task"],
                    language=arguments.get("language", "python"),
                    context=arguments.get("context", "")
                )
            
            else:
                return f"Unknown tool: {tool_name}"
        
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
            # Call the coder model directly (no tools needed for specialist)
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
    
    def chat(self, user_message: str) -> str:
        """
        Send a message to the agent and get a response
        
        Args:
            user_message: The user's message
            
        Returns:
            The agent's response as a string
        """
        logger.info(f"Chat request: {user_message[:50]}...")
        
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        try:
            # Always use orchestrator model
            response = ollama.chat(
                model=self.orchestrator_model,
                messages=self.conversation_history,
                tools=self.tools
            )
            
            # Check if model wants to use tools
            assistant_message = response['message']
            self.conversation_history.append(assistant_message)
            
            if assistant_message.get('tool_calls'):
                logger.info(f"Orchestrator requested {len(assistant_message['tool_calls'])} tool calls")
                
                # Execute each tool call
                for tool_call in assistant_message['tool_calls']:
                    function_name = tool_call['function']['name']
                    function_args = tool_call['function']['arguments']
                    
                    # Execute tool (might call code assistant)
                    tool_result = self._execute_tool(function_name, function_args)
                    
                    # Add tool result to conversation
                    self.conversation_history.append({
                        'role': 'tool',
                        'content': tool_result
                    })
                
                # Get final response from orchestrator with tool results
                final_response = ollama.chat(
                    model=self.orchestrator_model,
                    messages=self.conversation_history
                )
                
                final_message = final_response['message']
                self.conversation_history.append(final_message)
                
                return final_message['content']
            
            else:
                # No tool calls, return direct response
                return assistant_message['content']
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Conversation history reset")
    
    def get_history(self) -> List[Dict]:
        """
        Get conversation history as serializable dicts
        
        Returns:
            List of message dictionaries
        """
        history_serializable = []
        for msg in self.conversation_history:
            if hasattr(msg, 'model_dump'):  # Pydantic model
                history_serializable.append(msg.model_dump())
            else:  # Already a dict
                history_serializable.append(msg)
        return history_serializable
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information
        
        Returns:
            Dictionary with agent settings and status
        """
        return {
            'orchestrator_model': self.orchestrator_model,
            'coder_model': self.coder_model,
            'available_tools': [tool['function']['name'] for tool in self.tools],
            'conversation_length': len(self.conversation_history)
        }