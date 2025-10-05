"""CLI Interface for Local Agent using Typer and Rich"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

from agent_controller.agent import LocalAgent
from shared.config import ORCHESTRATOR_MODEL, CODER_MODEL

console = Console()
app = typer.Typer(
    name="agent",
    help="🤖 Local Agent - AI assistant with tool support",
    add_completion=False
)

_agent_instance: Optional[LocalAgent] = None


def get_agent() -> LocalAgent:
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = LocalAgent(
            orchestrator_model=ORCHESTRATOR_MODEL,
            coder_model=CODER_MODEL
        )
    return _agent_instance


def render_response(response: str):
    """Render agent response with markdown support - no frame for easy copying"""
    # Add visual separator before response
    console.print(Rule(title="🤖 Agent Response", style="bold green"))
    console.print()  # Empty line
    
    # Check if response contains markdown
    has_code_blocks = "```" in response
    has_headers = any(line.startswith('#') for line in response.split('\n'))
    has_lists = any(line.strip().startswith(('-', '*', '1.')) for line in response.split('\n'))
    
    if has_code_blocks or has_headers or has_lists:
        # Render as markdown with left padding
        md = Markdown(response)
        console.print(md, style="white")
    else:
        # Render as plain text with left padding and subtle styling
        console.print(response, style="white")
    
    console.print()  # Empty line
    # Add visual separator after response
    console.print(Rule(style="green"))


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send to the agent")
):
    """Send a single message to the agent"""
    agent = LocalAgent(
        orchestrator_model=ORCHESTRATOR_MODEL,
        coder_model=CODER_MODEL
    )
    
    try:
        with console.status("[bold green]🤔 Agent is thinking and using tools..."):
            response = agent.chat(message)
        
        render_response(response)
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def interactive():
    """Start interactive chat mode"""
    agent = get_agent()
    
    # Welcome banner
    console.print(Panel.fit(
        "[bold cyan]🤖 Local Agent - Interactive Mode[/bold cyan]\n\n"
        "[dim]Commands:[/dim] exit, quit, reset, history, info, clear\n"
        "[dim]Tools:[/dim] file_read, file_write, list_directory, code_assistant, web_search",
        border_style="cyan"
    ))
    
    while True:
        try:
            user_input = console.input("\n[bold blue]💬 You:[/bold blue] ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit']:
                console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            
            if user_input.lower() == 'reset':
                agent.reset()
                console.print("\n[green]✅ Conversation history cleared.[/green]")
                continue
            
            if user_input.lower() == 'history':
                display_history(agent)
                continue
            
            if user_input.lower() == 'info':
                display_info(agent)
                continue
            
            if user_input.lower() == 'clear':
                console.clear()
                console.print(Panel.fit(
                    "[bold cyan]🤖 Local Agent - Interactive Mode[/bold cyan]\n\n"
                    "[dim]Commands:[/dim] exit, quit, reset, history, info, clear\n"
                    "[dim]Tools:[/dim] file_read, file_write, list_directory, code_assistant, web_search",
                    border_style="cyan"
                ))
                continue
            
            # Get response from agent
            try:
                with console.status("[bold green]🤔 Agent is thinking and using tools..."):
                    response = agent.chat(user_input)
                
                render_response(response)
            
            except Exception as e:
                console.print(f"\n[red]❌ Error: {e}[/red]")
        
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]")
            break
        except EOFError:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]")
            break


@app.command()
def history():
    """Show conversation history"""
    agent = get_agent()
    display_history(agent)


@app.command()
def info():
    """Show agent information and status"""
    agent = get_agent()
    display_info(agent)


@app.command()
def reset():
    """Reset conversation history"""
    agent = get_agent()
    agent.reset()
    console.print("[green]✅ Conversation history cleared.[/green]")


def display_history(agent: LocalAgent):
    """Display conversation history in a table with markdown support"""
    history = agent.get_history()
    
    if not history:
        console.print("\n[yellow]📜 No conversation history yet.[/yellow]")
        return
    
    console.print()  # Empty line
    table = Table(title="📜 Conversation History", show_lines=True, expand=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Role", style="magenta", width=10)
    table.add_column("Content", style="white", ratio=3)
    table.add_column("Tools", style="yellow", width=20)
    
    for i, msg in enumerate(history, 1):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        
        # Format content preview
        if len(content) > 150:
            content_preview = content[:147] + "..."
        else:
            content_preview = content
        
        # Show markdown indicator
        if "```" in content or content.startswith('#'):
            content_preview = f"📝 {content_preview}"
        
        tool_calls = msg.get('tool_calls', [])
        tools_str = ", ".join([tc['function']['name'] for tc in tool_calls]) if tool_calls else "-"
        
        table.add_row(str(i), role, content_preview, tools_str)
    
    console.print(table)
    console.print("\n[dim]💡 Tip: Messages may be truncated in this view. Full content is preserved in conversation.[/dim]\n")


def display_info(agent: LocalAgent):
    """Display agent information"""
    info = agent.get_info()
    
    console.print()  # Empty line
    console.print(Rule(title="🔧 Agent Information", style="cyan"))
    console.print()
    
    # Create info table
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column(style="cyan bold", width=25)
    info_table.add_column(style="white")
    
    info_table.add_row("Orchestrator Model", f"[green]{info['orchestrator_model']}[/green]")
    info_table.add_row("Coder Model", f"[green]{info['coder_model']}[/green]")
    info_table.add_row("Available Tools", f"[yellow]{len(info['available_tools'])}[/yellow] tools")
    info_table.add_row("Messages in History", f"[yellow]{info['conversation_length']}[/yellow] messages")
    info_table.add_row("Max Iterations", f"[yellow]{info.get('max_iterations', 'N/A')}[/yellow]")
    
    console.print(info_table)
    
    console.print()
    console.print("[cyan bold]Available Tools:[/cyan bold]")
    for tool in info['available_tools']:
        console.print(f"  • [green]{tool}[/green]")
    
    console.print()
    console.print(Rule(style="cyan"))


if __name__ == "__main__":
    app()