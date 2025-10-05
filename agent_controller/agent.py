"""Agent Controller - Single orchestrator agent that delegates coding tasks"""

import logging
from typing import Dict, List, Any, Optional
import ollama

from agent_controller.mcp_client import MCPClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalAgent:
    """
    Local AI agent - Single orchestrator that delegates tasks
    
    Architecture:
    - Main agent (orchestrator) handles all interactions
    - Delegates coding tasks to specialized coder model
    - Uses MCP tools for file operations
    """
    
    def __init__(self, 
                 orchestrator_model: str = "llama3.1:8b", 
                 coder_model: str = "qwen2.5-coder:7b"):
        self.orchestrator_model = orchestrator_model
        self.coder_model = coder_model
        self.mcp_client = MCPClient()
        self.conversation_history: List[Any] = []
        self.tools = self._get_tool_definitions()
        logger.info(f"LocalAgent initialized - Orchestrator: {orchestrator_model}, Coder: {coder_model}")
    
    def _get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions including code delegation"""
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
                    'name': 'delegate_to_coder',
                    'description': 'Delegate a coding task to the specialized coder model. Use this for writing code, debugging, refactoring, or any programming-related task.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'task': {
                                'type': 'string',
                                'description': 'Clear description of the coding task to perform'
                            },
                            'context': {
                                'type': 'string',
                                'description': 'Optional additional context or requirements for the task'
                            }
                        },
                        'required': ['task']
                    }
                }
            }
        ]
    
    def _delegate_to_coder(self, task: str, context: str = "") -> str:
        """
        Delegate a coding task to the specialized coder model
        
        Args:
            task: Description of the coding task
            context: Additional context or requirements
            
        Returns:
            Code or response from the coder model
        """
        logger.info(f"Delegating to coder model: {task}")
        
        # Build prompt for coder model
        prompt = f"{task}"
        if context:
            prompt += f"\n\nAdditional context: {context}"
        
        try:
            # Call coder model (simple, no tool calling)
            response = ollama.chat(
                model=self.coder_model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            coder_response = response['message']['content']
            logger.info(f"Coder model completed task")
            return coder_response
        
        except Exception as e:
            logger.error(f"Error delegating to coder: {e}")
            return f"Error in coder model: {str(e)}"
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """Execute a tool call"""
        logger.info(f"Executing tool: {tool_name}")
        
        try:
            # Handle code delegation
            if tool_name == "delegate_to_coder":
                task = arguments.get("task", "")
                context = arguments.get("context", "")
                return self._delegate_to_coder(task, context)
            
            # Handle MCP tools (file operations)
            else:
                return self.mcp_client.call_tool(tool_name, arguments)
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error: {str(e)}"
    
    def chat(self, user_message: str) -> str:
        """
        Send a message to the agent and get a response
        
        The orchestrator agent:
        1. Receives user message
        2. Decides if it needs tools (files, code delegation)
        3. Executes tools as needed
        4. Returns final response
        
        Args:
            user_message: The user's message
            
        Returns:
            The agent's response as a string
        """
        logger.info(f"Orchestrator processing: {user_message[:50]}...")
        
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        try:
            # Call orchestrator with tools
            response = ollama.chat(
                model=self.orchestrator_model,
                messages=self.conversation_history,
                tools=self.tools
            )
            
            assistant_message = response['message']
            self.conversation_history.append(assistant_message)
            
            # Check if orchestrator wants to use tools
            if assistant_message.get('tool_calls'):
                logger.info(f"Orchestrator requested {len(assistant_message['tool_calls'])} tool calls")
                
                # Execute each tool call
                for tool_call in assistant_message['tool_calls']:
                    function_name = tool_call['function']['name']
                    function_args = tool_call['function']['arguments']
                    
                    # Execute tool (could be MCP tool or code delegation)
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