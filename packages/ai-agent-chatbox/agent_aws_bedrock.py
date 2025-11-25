"""
Thai Phung - AI Agent with Session Management and State
"""

from strands import Agent
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
import os
from dotenv import load_dotenv
import boto3

# Load environment variables from .env file
load_dotenv()


AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_SESSION_TOKEN = ""


class ChatAgent:
    """AI Agent with session management and conversation state"""

    def __init__(self, session_id: str = "default-session"):
        # Validate AWS credentials
        # aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        # aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        # aws_session_token = os.getenv("AWS_SESSION_TOKEN")
        aws_key = AWS_ACCESS_KEY_ID
        aws_secret = AWS_SECRET_ACCESS_KEY
        aws_session_token = AWS_SESSION_TOKEN
        aws_region = "eu-west-1"

        if not aws_key or not aws_secret or not aws_session_token:
            raise ValueError(
                "AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
            )

        print(f"[DEBUG] AWS_ACCESS_KEY_ID: {aws_key}...")
        print(f"[DEBUG] AWS_ACCESS_KEY_ID: {aws_secret}...")
        print(f"[DEBUG] AWS_REGION: {aws_region}")

        # Create boto3 session with credentials
        boto_session = boto3.Session(
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            aws_session_token=aws_session_token,
            region_name=aws_region,
        )

        # Configure Bedrock model
        self.model = BedrockModel(
            # model_id="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_id="eu.anthropic.claude-sonnet-4-20250514-v1:0",
            boto_session=boto_session,
            temperature=0.7,
            streaming=True,
            # region_name="eu-west-1",
        )

        # System prompt
        system_prompt = """You are a helpful AI assistant in a chatbox application.
You provide clear, concise, and friendly responses to user questions.
You maintain context across the conversation and can reference previous messages.
Always be polite and professional."""

        # Session manager for conversation history and state
        self.session_manager = FileSessionManager(
            session_id=session_id, storage_dir="./sessions"
        )

        # Create agent with session management
        self.agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            session_manager=self.session_manager,
            callback_handler=None,  # Disable default console output
        )

    def chat(self, user_message: str) -> str:
        """Send message to agent and get response"""
        result = self.agent(user_message)
        return result.message["content"][0]["text"]

    def get_conversation_history(self):
        """Get conversation history from agent"""
        return self.agent.messages
