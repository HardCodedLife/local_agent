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
        self.max_iterations = 10  # Prevent infinite loops
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
            # Get tools from MCP client
            tools = self.mcp_client.get_tool_definitions()
            
            # Multi-step execution loop
            iteration = 0
            while iteration < self.max_iterations:
                iteration += 1
                logger.info(f"Iteration {iteration}/{self.max_iterations}")
                
                # Call orchestrator with tools
                response = ollama.chat(
                    model=self.orchestrator_model,
                    messages=self.conversation_history,
                    tools=tools
                )
                
                assistant_message = response['message']
                self.conversation_history.append(assistant_message)
                
                # Check if model wants to use tools
                if assistant_message.get('tool_calls'):
                    logger.info(f"Orchestrator requested {len(assistant_message['tool_calls'])} tool calls")
                    
                    # Execute each tool call
                    for tool_call in assistant_message['tool_calls']:
                        function_name = tool_call['function']['name']
                        function_args = tool_call['function']['arguments']
                        
                        # Execute tool via MCP client
                        tool_result = self.mcp_client.call_tool(function_name, function_args)
                        
                        logger.info(f"Tool result length: {len(tool_result)} chars")
                        
                        # Add tool result to conversation
                        self.conversation_history.append({
                            'role': 'tool',
                            'content': tool_result
                        })
                    
                    # Continue loop - model may want to call more tools
                    continue
                
                else:
                    # No more tool calls - we have final response
                    final_content = assistant_message.get('content', '')
                    
                    if not final_content or final_content.strip() == '':
                        logger.warning("Model returned empty response!")
                        # Check if there's a 'thinking' field
                        thinking = assistant_message.get('thinking', '')
                        if thinking:
                            logger.info(f"Model thinking: {thinking}")
                            return f"The agent is still processing. Last thought: {thinking}"
                        return "Error: Model returned empty response after tool execution."
                    
                    logger.info(f"Final response generated after {iteration} iterations")
                    return final_content
            
            # Max iterations reached
            logger.warning(f"Max iterations ({self.max_iterations}) reached")
            return "Error: Maximum number of tool execution steps reached. The task may be too complex."
        
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
            'conversation_length': len(self.conversation_history),
            'max_iterations': self.max_iterations
        }