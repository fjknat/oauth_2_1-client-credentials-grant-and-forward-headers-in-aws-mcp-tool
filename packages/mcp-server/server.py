import jwt
import subprocess
import json
import sys
from fastmcp import FastMCP, Context
from typing import Optional
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError
from fastmcp.utilities.types import Image, Audio, File
import contextvars

# Context variable to store request authentication data
auth_context_var = contextvars.ContextVar("auth_context", default=(None, None))

# Configuration
JWT_SECRET = "your-secret-key"
API_BASE_URL = "http://localhost:3006"
PORT = 3005

# Initialize FastMCP server
mcp = FastMCP(name="ThaiInternalMCP", version="0.1.0")

# Global context for authentication
auth_context = {}

class AuthMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):

        jwt_token, tenant_id = get_request_context()
        print("- header: ", jwt_token, tenant_id)

        # Authentication check
        is_valid, message = validate_auth(jwt_token, tenant_id)

        if not is_valid:
            raise ToolError(f"Access denied: Authentication failed: {message}")

        # Set context for tools to use
        token = auth_context_var.set((jwt_token, tenant_id))
        try:
            # Allow other tools to proceed
            return await call_next(context)
        finally:
            auth_context_var.reset(token)

mcp.add_middleware(AuthMiddleware())

def verify_jwt_token(token: str) -> bool:
    """Verify JWT token validity"""
    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return True
    except jwt.InvalidTokenError:
        return False


def get_request_context() -> tuple[str, str]:
    """Get JWT token and tenant ID from request headers"""
    # Get headers (returns empty dict if no request context)
    headers = get_http_headers()
    print(headers)
    jwt_token = headers.get("x-jwt-token", "")
    tenant_id = headers.get("x-tenant-id", "")
    return jwt_token, tenant_id


def validate_auth(
    jwt_token: Optional[str], tenant_id: Optional[str]
) -> tuple[bool, str]:
    """Validate JWT token and tenant ID"""
    if not jwt_token:
        return False, "JWT token is required"

    if not verify_jwt_token(jwt_token):
        return False, "Invalid or expired JWT token"

    if tenant_id != "test123":
        return False, "Invalid tenant ID"

    return True, "Authentication successful"


@mcp.tool()
async def get_email(account_id: str,) -> dict:
    """
    Get email address for an account

    Args:
        account_id: Account ID (5-10 digits)
    """
    print(
        f"[MCP] get_email called - account_id: {account_id}",
        file=sys.stderr,
    )
    # Retrieve auth context from middleware
    jwt_token, tenant_id = auth_context_var.get()
    
    # If middleware didn't run (e.g. direct call or misconfiguration), try to get it directly
    if not jwt_token:
        jwt_token, tenant_id = get_request_context()

    # Authentication check
    # is_valid, message = validate_auth(jwt_token, tenant_id)
    # if not is_valid:
    #     print(f"[MCP] Authentication failed: {message}", file=sys.stderr)
    #     return f"Authentication failed: {message}"

    # Call REST API using curl
    try:

        
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-X",
                "GET",
                f"{API_BASE_URL}/get_email/{account_id}",
                "-H",
                f"Authorization: Bearer {jwt_token}",
                "-H",
                f"x-cdl-tenant-id: {tenant_id}",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "message" in data and "email" in data:
                print(
                    f"[MCP] Email retrieved successfully: {data['email']} for account {data['account_id']}",
                    file=sys.stderr,
                )
                return {
                    "status": "success",
                    "email": data['email'],
                    "account_id": data['account_id']
                }
            else:
                error_msg = data.get("message", "Unknown error")
                print(f"[MCP] API error: {error_msg}", file=sys.stderr)
                return {"status": "error", "message": error_msg}
        else:
            print(f"[MCP] Curl error: {result.stderr}", file=sys.stderr)
            return {"status": "error", "message": f"Failed to call API: {result.stderr}"}
    except Exception as e:
        print(f"[MCP] Connection error: {str(e)}", file=sys.stderr)
        return {"status": "error", "message": f"Failed to connect to API server: {str(e)}"}


@mcp.tool()
async def change_email(
    account_id: str,
    new_email: Optional[str] = None,
    user_confirmation: Optional[str] = None,
    ctx: Context = None,
) -> dict:
    """
    Change email address for an account (Human-in-the-loop workflow)

    Workflow:
    Step 1: If new_email is not provided, request it from AI Agent
    Step 2: If new_email is provided but no confirmation, ask user for Y/N confirmation
    Step 3: If confirmed (Y), call REST API to change email

    Args:
        account_id: Account ID (5-10 digits)
        new_email: New email address (optional, will be requested if not provided)
        user_confirmation: User confirmation Y/N (optional, will be requested)
    """
    print(
        f"[MCP] change_email called - account_id: {account_id}, new_email: {new_email}, confirmation: {user_confirmation}",
        file=sys.stderr,
    )

    # Retrieve auth context from middleware
    jwt_token, tenant_id = auth_context_var.get()

    # If middleware didn't run, try to get it directly
    if not jwt_token:
        jwt_token, tenant_id = get_request_context()

    # # Authentication check
    # is_valid, message = validate_auth(jwt_token, tenant_id)
    # if not is_valid:
    #     print(f"[MCP] Authentication failed: {message}", file=sys.stderr)
    #     return f"Authentication failed: {message}"

    # Step 1: Check if new_email is provided
    if not new_email:
        print(
            "[MCP] Step 1: Requesting new email from AI Agent", file=sys.stderr
        )
        return {
            "status": "pending",
            "step": "request_email",
            "message": "Please provide the new email address to proceed with the email change."
        }

    # Step 2: Check if user confirmation is provided
    if not user_confirmation:
        print(
            f"[MCP] Step 2: Requesting user confirmation for {new_email}",
            file=sys.stderr,
        )
        return {
            "status": "pending",
            "step": "confirmation",
            "message": f"Are you sure you want to change the email for account {account_id} to {new_email}? Please confirm (Y/N).",
            "account_id": account_id,
            "new_email": new_email
        }

    # Step 3: Process confirmation
    if user_confirmation.upper() != "Y":
        if ctx:
            result = await ctx.elicit(
                message="Are you sure you want to change the email again T/F?",
                response_type=str
            )
            if result.action == "T":
                return {"status": "success", "message": "Email changed successfullly by user."}
            else:
                return {"status": "cancelled", "message": "Email change cancelled by user."}
        print("[MCP] Step 3: Email change cancelled by user", file=sys.stderr)
        return {"status": "cancelled", "message": "Email change cancelled by user."}

    # Call REST API to change email using curl
    try:
        payload = json.dumps(
            {"account_id": account_id, "new_email": new_email}
        )
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-X",
                "POST",
                f"{API_BASE_URL}/change_email",
                "-H",
                f"Authorization: Bearer {jwt_token}",
                "-H",
                f"x-cdl-tenant-id: {tenant_id}",
                "-H",
                "Content-Type: application/json",
                "-d",
                payload,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            if (
                "message" in data
                and data["message"] == "Email changed successfully"
            ):
                print(
                    f"[MCP] Step 3: Email changed successfully - {data['account_id']} -> {data['new_email']}",
                    file=sys.stderr,
                )
                return {
                    "status": "success",
                    "message": f"Email changed successfully! Account {data['account_id']} now has email: {data['new_email']}",
                    "account_id": data['account_id'],
                    "new_email": data['new_email']
                }
            else:
                error_msg = data.get("message", "Unknown error")
                print(f"[MCP] API error: {error_msg}", file=sys.stderr)
                return {"status": "error", "message": error_msg}
        else:
            print(f"[MCP] Curl error: {result.stderr}", file=sys.stderr)
            return {"status": "error", "message": f"Failed to call API: {result.stderr}"}
    except Exception as e:
        print(f"[MCP] Connection error: {str(e)}", file=sys.stderr)
        return {"status": "error", "message": f"Failed to connect to API server: {str(e)}"}

@mcp.tool
def get_chart() -> Image:
    """Generate a chart image."""
    return Image(path="image01.png")

@mcp.tool
def get_multiple_charts() -> list[Image]:
    """Return multiple charts."""
    return [Image(path="image01.png"), Image(path="image02.png")]

if __name__ == "__main__":
    print(f"[MCP] Starting MCP Server on port {PORT}...", file=sys.stderr)
    print(f"[MCP] Transport: SSE", file=sys.stderr)
    print(f"[MCP] API Server: {API_BASE_URL}", file=sys.stderr)
    mcp.run(transport="http", host="localhost", port=PORT)
