"""Simple test script for MCP server using FastMCP Client"""
import asyncio
import subprocess
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

API_SERVER_URL = "http://localhost:3006"


def get_jwt_token():
    """Get JWT token from API server using curl"""
    try:
        result = subprocess.run(
            ["curl", "-s", f"{API_SERVER_URL}/generate-token"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data["token"]
        else:
            print(f"❌ Curl error: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Cannot get token: {e}")
        return None


async def main():
    """Run all tests"""
    print("🧪 MCP Server Test Suite")
    print("=" * 50)
    
    # Step 1: Get JWT token
    print("\n[1] Getting JWT token from API server...")
    token = get_jwt_token()
    if not token:
        print("❌ Failed to get JWT token")
        return
    print(f"✅ Got JWT token: {token[:20]}...")
    
    tenant_id = "test123"
    
    try:
        # Step 2: Connect to MCP server via stdio
        print(f"\n[2] Connecting to MCP server...")
        
        server_params = StdioServerParameters(
            command="python",
            args=["server.py"],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected to MCP server")
                
                # Step 3: List tools
                print("\n[3] Listing available tools...")
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description[:60] if tool.description else ''}...")
                
                # Step 4: Test get_email
                print("\n[4] Testing get_email tool...")
                result = await session.call_tool(
                    "get_email",
                    arguments={
                        "account_id": "12345",
                        "jwt_token": token,
                        "tenant_id": tenant_id
                    }
                )
                print(f"✅ Result: {result.content}")
                
                # Step 5: Test change_email (Step 1 - no email)
                print("\n[5] Testing change_email - Step 1 (no email)...")
                result = await session.call_tool(
                    "change_email",
                    arguments={
                        "account_id": "12345",
                        "jwt_token": token,
                        "tenant_id": tenant_id
                    }
                )
                print(f"✅ Result: {result.content}")
                
                # Step 6: Test change_email (Step 2 - request confirmation)
                print("\n[6] Testing change_email - Step 2 (request confirmation)...")
                result = await session.call_tool(
                    "change_email",
                    arguments={
                        "account_id": "12345",
                        "jwt_token": token,
                        "tenant_id": tenant_id,
                        "new_email": "newemail@example.com"
                    }
                )
                print(f"✅ Result: {result.content}")
                
                # Step 7: Test change_email (Step 3 - confirmed)
                print("\n[7] Testing change_email - Step 3 (confirmed Y)...")
                result = await session.call_tool(
                    "change_email",
                    arguments={
                        "account_id": "12345",
                        "jwt_token": token,
                        "tenant_id": tenant_id,
                        "new_email": "newemail@example.com",
                        "user_confirmation": "Y"
                    }
                )
                print(f"✅ Result: {result.content}")
                
                print("\n" + "=" * 50)
                print("✅ All tests completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
