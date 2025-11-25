"""
Thai Phung - AI Agent with Gemini Model
"""

from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models.gemini import GeminiModel
from strands.session.file_session_manager import FileSessionManager
import os
from dotenv import load_dotenv
from strands.tools.mcp import MCPClient

load_dotenv()

# Cache for auth headers
cache = {"jwt_token": None, "tenant_id": None}


class GeminiChatAgent:
    """AI Agent using Gemini model"""

    def __init__(self, session_id: str = "default-session"):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        # print(f"[DEBUG] GEMINI_API_KEY: {api_key}...")

        self.model = GeminiModel(
            model_id="gemini-2.0-flash",
            client_args={
                "api_key": api_key,
            },
            params={
                # some sample model parameters
                "temperature": 0.7,
                "max_output_tokens": 2048,
                "top_p": 0.9,
                "top_k": 40,
            },
        )

        system_prompt = """You are a helpful AI assistant in a chatbox application.
You provide clear, concise, and friendly responses to user questions.
You maintain context across the conversation and can reference previous messages.
Always be polite and professional."""

        self.session_manager = FileSessionManager(
            session_id=session_id, storage_dir="./sessions"
        )

        # Configure MCP Client with headers from cache
        headers_value = {}
        if cache["jwt_token"]:
            headers_value["X-JWT-TOKEN"] = cache["jwt_token"]
        if cache["tenant_id"]:
            headers_value["X-TENANT-ID"] = cache["tenant_id"]

        self.mcp_client = MCPClient(lambda: streamablehttp_client(
            url="http://127.0.0.1:3005/mcp",
            headers=headers_value
        ))

        self.agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            session_manager=self.session_manager,
            callback_handler=None,
            tools=[self.mcp_client],
        )

    def chat(self, user_message: str) -> str:
        """Send message to agent and get response"""
        result = self.agent(user_message)
        return result.message["content"][0]["text"]

    def get_conversation_history(self):
        """Get conversation history from agent"""
        return self.agent.messages
