"""Model routing logic - selects appropriate model based on task"""

from typing import List

class ModelRouter:
    """Routes tasks to appropriate models"""
    
    def __init__(self, default_model: str, coder_model: str):
        self.default_model = default_model
        self.coder_model = coder_model
        self.coding_keywords = [
            "code", "program", "script", "function", "debug", 
            "implement", "write a", "create a", "algorithm",
            "class", "method", "variable", "refactor"
        ]
    
    def select_model(self, user_message: str) -> str:
        """
        Select appropriate model based on user message
        
        Args:
            user_message: The user's input message
            
        Returns:
            Model name to use
        """
        message_lower = user_message.lower()
        
        # Check for coding keywords
        for keyword in self.coding_keywords:
            if keyword in message_lower:
                return self.coder_model
        
        # Default model for general tasks
        return self.default_model
    
    def add_coding_keyword(self, keyword: str):
        """Add a custom coding keyword"""
        if keyword.lower() not in self.coding_keywords:
            self.coding_keywords.append(keyword.lower())
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return [self.default_model, self.coder_model]