"""Shared configuration for the local agent system"""

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"

# Model configuration
ORCHESTRATOR_MODEL = "gpt-oss:120b-cloud"  #"granite4:micro-h"  # Main agent that orchestrates
CODER_MODEL = "qwen3-coder:480b-cloud"    #"deepcoder:1.5b" # Specialist for coding tasks

# MCP Server settings
MCP_SERVER_HOST = "localhost"
MCP_SERVER_PORT = 8000

# Paths
DATA_DIR = "data"
MEMORY_DB = "data/memory.db"
LOG_DIR = "data/logs"