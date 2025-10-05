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

from agent_controller.agent import LocalAgent
from shared.config import DEFAULT_MODEL, CODER_MODEL

# Rest of your CLI code stays the same...
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
            default_model=DEFAULT_MODEL,
            coder_model=CODER_MODEL
        )
    return _agent_instance


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send to the agent"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model selection")
):
    """Send a single message to the agent"""
    agent = LocalAgent(default_model=DEFAULT_MODEL, coder_model=CODER_MODEL)
    
    try:
        with console.status("[bold green]Agent is thinking..."):
            response = agent.chat(message, model_override=model)
        
        console.print(Panel(response, title="🤖 Agent Response", border_style="green"))
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def interactive():
    """Start interactive chat mode"""
    agent = get_agent()
    
    console.print(Panel.fit(
        "[bold cyan]🤖 Local Agent - Interactive Mode[/bold cyan]\n\n"
        "Commands:\n"
        "  • [yellow]exit/quit[/yellow] - Exit the program\n"
        "  • [yellow]reset[/yellow] - Clear conversation history\n"
        "  • [yellow]history[/yellow] - Show conversation\n"
        "  • [yellow]info[/yellow] - Show agent information\n\n"
        "Tools: file_read, file_write, list_directory",
        border_style="cyan"
    ))
    
    while True:
        try:
            user_input = console.input("\n[bold blue]💬 You:[/bold blue] ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
            
            if user_input.lower() == 'reset':
                agent.reset()
                console.print("[green]✅ Conversation history cleared.[/green]")
                continue
            
            if user_input.lower() == 'history':
                display_history(agent)
                continue
            
            if user_input.lower() == 'info':
                display_info(agent)
                continue
            
            try:
                with console.status("[bold green]🤔 Agent is thinking..."):
                    response = agent.chat(user_input)
                
                console.print(Panel(response, title="🤖 Agent", border_style="green"))
            
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break
        except EOFError:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
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
    """Display conversation history in a table"""
    history = agent.get_history()
    
    if not history:
        console.print("[yellow]📜 No conversation history yet.[/yellow]")
        return
    
    table = Table(title="📜 Conversation History", show_lines=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Role", style="magenta", width=10)
    table.add_column("Content", style="white")
    table.add_column("Tools", style="yellow", width=20)
    
    for i, msg in enumerate(history, 1):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        if len(content) > 100:
            content = content[:97] + "..."
        
        tool_calls = msg.get('tool_calls', [])
        tools_str = ", ".join([tc['function']['name'] for tc in tool_calls]) if tool_calls else "-"
        
        table.add_row(str(i), role, content, tools_str)
    
    console.print(table)


def display_info(agent: LocalAgent):
    """Display agent information"""
    info = agent.get_info()
    
    info_table = Table(title="🔧 Agent Information")
    info_table.add_column("Setting", style="cyan", width=20)
    info_table.add_column("Value", style="green")
    
    info_table.add_row("Default Model", info['default_model'])
    info_table.add_row("Coder Model", info['coder_model'])
    info_table.add_row("Current Model", info['current_model'])
    info_table.add_row("Available Tools", ", ".join(info['available_tools']))
    info_table.add_row("Messages in History", str(info['conversation_length']))
    
    console.print(info_table)


if __name__ == "__main__":
    app()