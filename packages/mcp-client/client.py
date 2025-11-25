"""
Thai Phung - MCP Client tool
"""

import asyncio
import base64
import subprocess
import json
from fastmcp import Client, FastMCP
from fastmcp.client.elicitation import ElicitResult
from fastmcp.client.transports import StreamableHttpTransport
from PIL import Image
from io import BytesIO

# Cache for JWT token and tenant ID
cache = {"jwt_token": None, "tenant_id": None}

MCP_SERVER_URL = "http://127.0.0.1:3005/mcp"


def print_logo():
    """Print simple logo on startup"""
    print(
        """
===========================================
     MCP CLIENT CHATBOX CLI
     FastMCP Integration
===========================================
    """
    )

async def elicitation_handler(message: str, response_type: type, params, context):
    # Present the message to the user and collect input
    user_input = input(f"{message}: ")
    
    # Create response using the provided dataclass type
    # FastMCP converted the JSON schema to this Python type for you
    response_data = response_type(value=user_input)
    
    # You can return data directly - FastMCP will implicitly accept the elicitation
    return response_data
    
    # Or explicitly return an ElicitResult for more control
    # return ElicitResult(action="accept", content=response_data)


def get_jwt_token():
    """Get JWT token from API server using curl"""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:3006/generate-token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data["token"]
        else:
            print(f"❌ Error getting token: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return None


async def list_mcp_info(client):
    """List tools, resources and prompts from MCP server"""
    print("\n📋 Fetching information from MCP Server...\n")

    # List tools
    tools = await client.list_tools()
    print("🔧 TOOLS:")
    if tools:
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    else:
        print("  No tools available")

    # List resources
    resources = await client.list_resources()
    print("\n📦 RESOURCES:")
    if resources:
        for resource in resources:
            print(f"  - {resource.uri}: {resource.name}")
    else:
        print("  No resources available")

    # List prompts
    prompts = await client.list_prompts()
    print("\n💬 PROMPTS:")
    if prompts:
        for prompt in prompts:
            print(f"  - {prompt.name}: {prompt.description}")
    else:
        print("  No prompts available")
    print()


async def call_get_email(client, account_id: str):
    """Call get_email tool"""

    result = await client.call_tool(
        "get_email",
        {
            "account_id": account_id
        }
    )
    print(f"\n✅ Result: {result.structured_content}\n")


async def call_get_chart(client):
    """Call get_email tool"""

    result = await client.call_tool(
        "get_chart",
    )
    # print(json.dumps(result.data, indent=2))
    # print(f"\n✅ Result: .... {result.content[0].data}\n")
    base64_data = result.content[0].data
    image_bytes = base64.b64decode(base64_data)

    img = Image.open(BytesIO(image_bytes))
    img.show()
    

async def call_change_email(client, account_id: str, new_email: str):
    """Call change_email tool with confirmation workflow"""
    # Step 1: Call with new_email
    result = await client.call_tool(
        "change_email",
        {
            "account_id": account_id,
            "new_email": new_email,
        }
    )
    print(f"\n📝 step 1:  {result}")

    # Step 2: If confirmation needed, ask user
    if "confirm" in str(result).lower():
        confirmation = input("Enter Y to confirm, N to cancel: ").strip()
        result = await client.call_tool(
            "change_email",
            {
            "account_id": account_id,
            "new_email": new_email,
            "user_confirmation": confirmation,
            }
        )
        print(f"\n✅ Result: {result}\n")


async def chatbox_loop(client):
    """Chatbox CLI loop"""
    print("\n💬 CHATBOX CLI - Type 'exit' to quit")
    print("Commands: get_email, change_email, get_chart\n")

    while True:
        try:
            command = input("👤 You: ").strip().lower()

            if command == "exit":
                print("👋 Goodbye!")
                break

            elif command in ["get_email","g"]:
                account_id = input("Enter account_id (5-10 digits): ").strip()
                await call_get_email(client, account_id)

            elif command in ["change_email","c"]:
                account_id = input("Enter account_id (5-10 digits): ").strip()
                new_email = input("Enter new email: ").strip()
                print(f"\n🎆 {new_email}")
                await call_change_email(client, account_id, new_email)

            elif command in ["get_chart","gc"]:
                await call_get_chart(client)

            else:
                print(
                    "❌ Invalid command. Please choose: get_email, change_email, or exit\n"
                )

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


async def main():
    """Main function"""
    import sys

    if sys.platform == "win32":
        import os

        os.system("chcp 65001 > nul")
    print_logo()

    # Ask if user wants to get JWT token
    get_token = (
        input("🔑 Do you want to get JWT token? (y/n): ").strip().lower()
    )
    if get_token == "y":
        token = get_jwt_token()
        if token:
            cache["jwt_token"] = token
            print(f"✅ Token saved to cache\n")
        else:
            print("⚠️ Cannot get token, continuing without token\n")

    # Enter tenant ID
    tenant_id = input("🏢 Enter tenant-id: ").strip()
    cache["tenant_id"] = tenant_id
    print(f"✅ Tenant ID saved: {tenant_id}\n")

    headers_value = {
        "X-JWT-TOKEN": cache["jwt_token"],
        "X-TENANT-ID": cache["tenant_id"]
    }

    transport = StreamableHttpTransport(
        MCP_SERVER_URL, 
        headers=headers_value,
    )

    # Connect to MCP server via FastMCP client
    async with Client(transport=transport, elicitation_handler=elicitation_handler) as client:

        # Display MCP information
        await list_mcp_info(client)

        # Start chatbox loop
        await chatbox_loop(client)


if __name__ == "__main__":
    asyncio.run(main())
