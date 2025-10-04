# Complete MCP Server Project Plan

## 🎯 **Project Overview**

You're building a **local AI agent system** with:
- **MCP Server**: Provides tools (file operations, web search, code execution, etc.)
- **Ollama**: Runs local LLMs that use these tools
- **Agent Controller**: Orchestrates model selection and task execution
- **Progressive development**: Start simple, add capabilities over time

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────┐
│                  YOU (User)                      │
└──────────────────┬──────────────────────────────┘
                   │ Natural language requests
                   ↓
┌─────────────────────────────────────────────────┐
│            Agent Controller (Python)             │
│  - Receives user requests                        │
│  - Routes to appropriate Ollama model            │
│  - Manages conversation context                  │
│  - Handles model switching                       │
└──────────┬──────────────────────┬────────────────┘
           │                      │
           ↓                      ↓
┌──────────────────┐    ┌─────────────────────┐
│  Ollama Server   │    │   MCP Server        │
│                  │    │   (Python/TypeScript)│
│ • llama3.1:8b    │◄───┤                     │
│ • qwen2.5:7b     │    │ Tools:              │
│ • qwen2.5-coder  │    │ • file_read         │
└──────────────────┘    │ • file_write        │
                        │ • web_search        │
                        │ • execute_code      │
                        │ • memory_store      │
                        └─────────────────────┘
```

---

## 📋 **Development Phases**

### **Phase 1: Foundation (Week 1-2)**
**Goal**: Get basic MCP server working with one tool

**Steps**:
1. **Set up MCP server** (Python first)
   - Install: `pip install mcp`
   - Create basic server with file_read tool
   - Test with MCP inspector

2. **Connect Ollama to MCP**
   - Use Ollama's function calling API
   - Test with llama3.1:8b
   - Verify tool execution works

3. **Build simple Agent Controller**
   - Python script that sends prompts to Ollama
   - Parses tool calls from Ollama
   - Executes tools via MCP
   - Returns results to Ollama

**Deliverable**: Ask agent "read file X" → it uses MCP to read → returns content

---

### **Phase 2: Core Tools (Week 3-4)**
**Goal**: Add essential tools for daily tasks

**Add these tools to MCP server**:
- `file_write(path, content)` - Write files
- `file_search(query, directory)` - Search file contents
- `list_directory(path)` - List files
- `execute_python(code)` - Run Python code safely
- `web_search(query)` - Search the web

**Deliverable**: Agent can manage files, search web, run code

---

### **Phase 3: Model Routing (Week 5)**
**Goal**: Intelligently route tasks to best model

**Agent Controller logic**:
```python
def route_task(user_input):
    if "code" in user_input.lower() or "program" in user_input.lower():
        return "qwen2.5-coder:7b"
    else:
        return "llama3.1:8b"
```

**Deliverable**: Coding tasks → Coder model, Others → General model

---

### **Phase 4: Memory & Context (Week 6-7)**
**Goal**: Agent remembers past interactions

**Add to MCP**:
- `memory_store(key, value)` - Save information
- `memory_retrieve(query)` - Recall information
- SQLite database for persistence

**Deliverable**: Agent remembers your preferences, past conversations

---

### **Phase 5: Advanced Features (Week 8+)**
**Progressive additions**:
- Email integration
- Calendar access
- GitHub operations
- Document parsing (PDF, etc.)
- Task scheduling
- Multi-step planning

---

## 💻 **Technical Implementation**

### **1. MCP Server Structure (Python)**

```python
# server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import os

server = Server("my-local-agent")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="file_read",
            description="Read contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"}
                },
                "required": ["path"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "file_read":
        path = arguments["path"]
        with open(path, 'r') as f:
            content = f.read()
        return [TextContent(type="text", text=content)]

# Run server
if __name__ == "__main__":
    server.run()
```

---

### **2. Agent Controller (Python)**

```python
# agent.py
import ollama
import json

class LocalAgent:
    def __init__(self, mcp_tools):
        self.mcp_tools = mcp_tools  # Your MCP server connection
        self.model = "llama3.1:8b"
        self.conversation = []
    
    def chat(self, user_message):
        self.conversation.append({
            'role': 'user',
            'content': user_message
        })
        
        # Send to Ollama with tools
        response = ollama.chat(
            model=self.model,
            messages=self.conversation,
            tools=self.get_tool_definitions()
        )
        
        # Handle tool calls
        if response['message'].get('tool_calls'):
            tool_results = self.execute_tools(response['message']['tool_calls'])
            # Send results back to model
            return self.chat_with_tool_results(tool_results)
        
        return response['message']['content']
    
    def execute_tools(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            # Call your MCP server here
            result = self.mcp_tools.call(
                tool_call['function']['name'],
                json.loads(tool_call['function']['arguments'])
            )
            results.append(result)
        return results
    
    def get_tool_definitions(self):
        # Get from your MCP server
        return self.mcp_tools.list_tools()

# Usage
agent = LocalAgent(mcp_connection)
response = agent.chat("Read the file config.json")
print(response)
```

---

### **3. How to Use the Agent**

**Option A: Command Line**
```bash
python agent.py
> Read my todo.txt file
> Search for Python files in /projects
> Write a script to analyze CSV data
```

**Option B: Web Interface** (later phase)
- Build simple Flask/FastAPI web UI
- Chat interface like ChatGPT
- Upload files, view results

**Option C: API** (for integration)
- Expose agent as REST API
- Call from other apps/scripts

---

## 🔧 **Setup Instructions**

### **Prerequisites**
```bash
# 1. Install Ollama
# Download from ollama.ai

# 2. Pull models
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:7b

# 3. Install Python dependencies
pip install mcp ollama requests
```

### **Quick Start**
```bash
# 1. Clone/create project
mkdir local-agent && cd local-agent

# 2. Create MCP server (server.py)
# 3. Create Agent controller (agent.py)

# 4. Run MCP server
python server.py

# 5. In another terminal, run agent
python agent.py
```

---

## 📊 **Success Metrics**

**Phase 1**: ✅ Tool execution works  
**Phase 2**: ✅ Can complete 5+ different task types  
**Phase 3**: ✅ Correct model selected 90%+ of time  
**Phase 4**: ✅ Remembers context across sessions  
**Phase 5**: ✅ Handles complex multi-step tasks  

---

## 🎓 **TypeScript Migration Path**

**Once Python version works:**
1. Rewrite MCP server in TypeScript using `@modelcontextprotocol/sdk`
2. Keep same tool definitions
3. Test compatibility with existing Agent Controller
4. Gradually migrate Agent Controller if desired

**Why wait**: Prove the architecture works first, then learn TypeScript while rebuilding something you understand.

---

## 📚 **Resources**

- **MCP Docs**: https://modelcontextprotocol.io
- **Ollama API**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk

---

**Ready to start?** I'd recommend beginning with Phase 1. Would you like me to provide the complete starter code for the MCP server and Agent Controller?