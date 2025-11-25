"""
Thai Phung - CLI Chatbox with Rich UI
"""

import sys
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text
from rich import box
from datetime import datetime
from agent_aws_bedrock import ChatAgent
from agent_gemini import GeminiChatAgent


class Chatbox:
    """CLI Chatbox with beautiful UI"""

    def __init__(
        self, session_id: str = "default-session", model: str = "bedrock"
    ):
        self.console = Console()
        self.model = model

        if model == "gemini":
            self.agent = GeminiChatAgent(session_id=session_id)
        else:
            self.agent = ChatAgent(session_id=session_id)

        self.conversation_count = 0

    def display_welcome(self):
        """Display welcome message"""
        model_name = (
            "Gemini 2.5 Flash"
            if self.model == "gemini"
            else "Bedrock (Claude 3.5 Sonnet)"
        )
        welcome_text = f"""
# 🤖 AI Agent Chatbox

Welcome to the AI-powered chatbox! 
Model: **{model_name}**

**Commands:**
- Type your message to chat
- Type 'exit' or 'quit' to end the session
- Type 'clear' to clear the screen
- Type 'history' to view conversation history
- Type 'switch' to change model (bedrock/gemini)
- Type 'auth' to setup authentication
        """
        self.console.print(
            Panel(
                Markdown(welcome_text),
                title="[bold cyan]Welcome[/bold cyan]",
                border_style="cyan",
                box=box.DOUBLE,
            )
        )
        self.console.print()

    def display_user_message(self, message: str):
        """Display user message"""
        self.conversation_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")

        user_panel = Panel(
            Text(message, style="white"),
            title=f"[bold green]👤 You[/bold green] [dim]({timestamp})[/dim]",
            title_align="left",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1),
        )
        self.console.print(user_panel)

    def display_ai_message(self, message: str):
        """Display AI response"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        ai_panel = Panel(
            Markdown(message),
            title=f"[bold blue]🤖 AI Assistant[/bold blue] [dim]({timestamp})[/dim]",
            title_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
        )
        self.console.print(ai_panel)
        self.console.print()  # Add spacing between conversations

    def display_error(self, error: str):
        """Display error message"""
        self.console.print(
            Panel(
                f"[red]{error}[/red]",
                title="[bold red]❌ Error[/bold red]",
                border_style="red",
            )
        )

    def display_info(self, info: str):
        """Display info message"""
        self.console.print(
            Panel(
                f"[yellow]{info}[/yellow]",
                title="[bold yellow]ℹ️  Info[/bold yellow]",
                border_style="yellow",
            )
        )

    def switch_model(self):
        """Switch between Bedrock and Gemini models"""
        new_model = "gemini" if self.model == "bedrock" else "bedrock"

        confirm = Prompt.ask(
            f"Switch from {self.model} to {new_model}?",
            choices=["y", "n"],
            default="n",
        )

        if confirm.lower() == "y":
            self.model = new_model

            if new_model == "gemini":
                self.agent = GeminiChatAgent(
                    session_id=self.agent.session_manager.session_id
                )
            else:
                self.agent = ChatAgent(
                    session_id=self.agent.session_manager.session_id
                )

            model_name = (
                "Gemini 2.5 Flash"
                if new_model == "gemini"
                else "Bedrock (Claude 3.5 Sonnet)"
            )
            self.console.print(
                f"\n[green]✓ Switched to {model_name}[/green]\n"
            )

    def display_history(self):
        """Display conversation history"""
        history = self.agent.get_conversation_history()

        if not history:
            self.display_info("No conversation history yet.")
            return

        self.console.print(
            Panel(
                f"[cyan]Total messages: {len(history)}[/cyan]",
                title="[bold cyan]📜 Conversation History[/bold cyan]",
                border_style="cyan",
            )
        )

        for idx, msg in enumerate(history, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", [])

            if content and isinstance(content, list) and len(content) > 0:
                text_content = content[0].get("text", "")
                role_emoji = "👤" if role == "user" else "🤖"
                role_name = "You" if role == "user" else "AI"
                role_color = "green" if role == "user" else "blue"

                self.console.print(
                    f"[{role_color}]{role_emoji} {role_name}:[/{role_color}] {text_content[:100]}..."
                )

        self.console.print()

    def run(self):
        """Run the chatbox"""
        self.display_welcome()

        while True:
            try:
                # Get user input
                user_input = Prompt.ask(
                    "[bold green]You[/bold green]", default=""
                ).strip()

                # Handle empty input
                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["exit", "quit"]:
                    self.console.print(
                        "\n[cyan]👋 Goodbye! Have a great day![/cyan]\n"
                    )
                    break

                if user_input.lower() == "clear":
                    self.console.clear()
                    self.display_welcome()
                    continue

                if user_input.lower() == "history":
                    self.display_history()
                    continue

                if user_input.lower() == "switch":
                    self.switch_model()
                    continue

                if user_input.lower() == "auth":
                    self.setup_auth()
                    continue

                # Display user message
                self.display_user_message(user_input)

                # Show thinking indicator
                with self.console.status(
                    "[bold blue]🤔 AI is thinking...[/bold blue]",
                    spinner="dots",
                ):
                    # Get AI response
                    response = self.agent.chat(user_input)

                # Display AI response
                self.display_ai_message(response)

            except KeyboardInterrupt:
                self.console.print(
                    "\n\n[cyan]👋 Goodbye! Have a great day![/cyan]\n"
                )
                break
            except Exception as e:
                self.display_error(f"An error occurred: {str(e)}")
                self.console.print(
                    "[dim]Press Ctrl+C to exit or continue chatting...[/dim]\n"
                )

    def setup_auth(self):
        """Setup authentication configuration"""
        import subprocess
        import json
        from agent_gemini import cache as gemini_cache

        self.console.print(
            Panel(
                "Setting up authentication configuration...",
                title="[bold yellow]🔐 Auth Setup[/bold yellow]",
                border_style="yellow",
            )
        )

        token = None
        # 1. Get JWT Token
        with self.console.status(
            "[bold blue]Fetching JWT token...[/bold blue]", spinner="dots"
        ):
            try:
                result = subprocess.run(
                    ["curl", "-s", "http://localhost:3006/generate-token"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    token = data.get("token")
                    if token:
                        self.console.print(f"[green]✅ JWT Token fetched successfully[/green]")
                    else:
                        self.console.print("[red]❌ Token not found in response[/red]")
                else:
                    self.console.print(f"[red]❌ Error getting token: {result.stderr}[/red]")
            except Exception as e:
                self.console.print(f"[red]❌ Cannot connect to API server: {e}[/red]")

        # 2. Get Tenant ID
        tenant_id = Prompt.ask(
            "Enter tenant-id", default="test123"
        )
        self.console.print(f"[green]✅ Tenant ID set to: {tenant_id}[/green]\n")
        
        # Update cache and re-initialize agent
        if token:
            gemini_cache["jwt_token"] = token
        gemini_cache["tenant_id"] = tenant_id

        self.console.print("[blue]🔄 Re-initializing agent with new credentials...[/blue]")
        if self.model == "gemini":
             self.agent = GeminiChatAgent(session_id=self.agent.session_manager.session_id)
             self.console.print("[green]✅ Agent re-initialized successfully[/green]\n")
        else:
             self.console.print("[yellow]⚠️  Auth update only supported for Gemini agent currently.[/yellow]\n")




def main():
    """Main entry point"""
    if sys.platform == "win32":
        import os
        os.system("chcp 65001 > nul")

    import argparse

    parser = argparse.ArgumentParser(description="AI Agent Chatbox")
    new_uuid = uuid.uuid4()
    parser.add_argument(
        "--session-id",
        type=str,
        default=str(new_uuid),
        help="Session ID for conversation persistence",
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["bedrock", "gemini"],
        default="gemini",
        help="Model: bedrock (Claude 3.5 Sonnet) or gemini (Gemini 2.5 Flash)",
    )

    args = parser.parse_args()

    chatbox = Chatbox(session_id=args.session_id, model=args.model)
    chatbox.run()


if __name__ == "__main__":
    main()
