"""MCP Server - Provides tools for the agent"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.types import Tool, TextContent

from mcp_server.tools import get_registry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server
server = Server("local-agent-mcp")

# Get tool registry
registry = get_registry()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools from registry"""
    tools = []
    
    for tool_name, tool_def in registry.tools.items():
        tools.append(
            Tool(
                name=tool_def['name'],
                description=tool_def['description'],
                inputSchema=tool_def['parameters']
            )
        )
    
    logger.info(f"Listed {len(tools)} tools")
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute tool calls via registry"""
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    try:
        # Call through registry
        result = registry.call_tool(name, arguments)
        return [TextContent(type="text", text=result)]
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    logger.info("Starting MCP server...")
    logger.info(f"Available tools: {', '.join(registry.list_tool_names())}")
    
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())