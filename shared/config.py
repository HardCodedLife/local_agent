"""Shared configuration for the local agent system"""

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"

# Model configuration
ORCHESTRATOR_MODEL = "gpt-oss:120b-cloud"  # Main agent that orchestrates everything, "granite4:micro-h", 
CODER_MODEL = "qwen3-coder:480b-cloud"    # Specialized coding model (delegated to), "deepcoder:1.5b"

# MCP Server settings
MCP_SERVER_HOST = "localhost"
MCP_SERVER_PORT = 8000

# Paths
DATA_DIR = "data"
MEMORY_DB = "data/memory.db"
LOG_DIR = "data/logs"