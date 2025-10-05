"""Shared configuration for the local agent system"""

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "granite4:micro-h"
CODER_MODEL = "deepcoder:1.5b"

# MCP Server settings
MCP_SERVER_HOST = "localhost"
MCP_SERVER_PORT = 8000

# Paths
DATA_DIR = "data"
MEMORY_DB = "data/memory.db"
LOG_DIR = "data/logs"

# Model routing keywords
CODING_KEYWORDS = ["code", "program", "script", "function", "debug", "implement", "write a", "create a"]