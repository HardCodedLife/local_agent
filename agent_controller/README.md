# Agent Controller

Core agent orchestration logic.

## Components
- `agent.py` - Main agent class
- `model_router.py` - Model selection
- `mcp_client.py` - MCP server communication

## Usage
```python
from agent_controller.agent import LocalAgent

agent = LocalAgent()
response = agent.chat("Hello!")