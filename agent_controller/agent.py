"""Agent Controller - Pure orchestration logic without UI"""

import logging
from typing import List, Any, Dict
import ollama

from agent_controller.mcp_client import MCPClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LocalAgent:
    """Local AI agent with tool support - Pure logic, no UI"""
    
    def __init__(self, orchestrator_model: str = "granite4:micro-h", coder_model: str = "deepcoder:1.5b"):
        self.orchestrator_model = orchestrator_model
        self.mcp_client = MCPClient(coder_model=coder_model)
        self.conversation_history: List[Any] = []
        logger.info(f"LocalAgent initialized - Orchestrator: {orchestrator_model}")
    
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
            # Get tools from MCP client (dynamically loaded!)
            tools = self.mcp_client.get_tool_definitions()
            
            # Call orchestrator with tools
            response = ollama.chat(
                model=self.orchestrator_model,
                messages=self.conversation_history,
                tools=tools
            )
            
            assistant_message = response['message']
            self.conversation_history.append(assistant_message)
            
            if assistant_message.get('tool_calls'):
                logger.info(f"Orchestrator requested {len(assistant_message['tool_calls'])} tool calls")
                
                # Execute each tool call via MCP client
                for tool_call in assistant_message['tool_calls']:
                    function_name = tool_call['function']['name']
                    function_args = tool_call['function']['arguments']
                    
                    # Execute tool via MCP client
                    tool_result = self.mcp_client.call_tool(function_name, function_args)
                    
                    # DEBUG: Log the tool result
                    logger.info(f"Tool result length: {len(tool_result)} chars")
                    logger.debug(f"Tool result preview: {tool_result[:200]}...")
                    
                    # Add tool result to conversation
                    self.conversation_history.append({
                        'role': 'tool',
                        'content': tool_result
                    })
                
                # DEBUG: Log conversation state before final call
                logger.info(f"Conversation history has {len(self.conversation_history)} messages")
                
                # Get final response from orchestrator
                final_response = ollama.chat(
                    model=self.orchestrator_model,
                    messages=self.conversation_history
                )
                
                final_message = final_response['message']
                final_content = final_message.get('content', '')
                
                # DEBUG: Check if response is empty
                if not final_content or final_content.strip() == '':
                    logger.warning("Model returned empty response!")
                    logger.warning(f"Final message: {final_message}")
                    return "Error: Model returned empty response. This might be a model capability issue."
                
                self.conversation_history.append(final_message)
                
                return final_content
            
            else:
                # No tool calls, return direct response
                return assistant_message.get('content', '')
        
        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            raise
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []
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
            'orchestrator_model': self.orchestrator_model,
            'coder_model': self.mcp_client.coder_model,
            'available_tools': self.mcp_client.list_tools(),
            'conversation_length': len(self.conversation_history)
        }