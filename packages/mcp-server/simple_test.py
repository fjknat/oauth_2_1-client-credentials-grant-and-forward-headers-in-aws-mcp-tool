"""Simple direct test without FastMCP Client"""
import subprocess
import json

API_SERVER_URL = "http://localhost:3006"
MCP_SERVER_URL = "http://localhost:3007"


def curl_request(url, method="GET", data=None, headers=None):
    """Make HTTP request using curl"""
    cmd = ["curl", "-s", "-X", method]
    
    if headers:
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json"])
        cmd.extend(["-d", json.dumps(data)])
    
    cmd.append(url)
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return result.stdout
    else:
        return None


def main():
    print("🧪 Simple MCP Server Test")
    print("=" * 50)
    
    # Step 1: Get JWT token
    print("\n[1] Getting JWT token...")
    response = curl_request(f"{API_SERVER_URL}/generate-token")
    if response and "token" in response:
        token = response["token"]
        print(f"✅ Got token: {token[:20]}...")
    else:
        print("❌ Failed to get token")
        return
    
    tenant_id = "test123"
    
    # Step 2: Test MCP server - List tools
    print("\n[2] Testing MCP server - List tools...")
    
    # Try different endpoints
    endpoints = ["/", "/sse", "/messages"]
    
    for endpoint in endpoints:
        print(f"   Trying endpoint: {endpoint}")
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        response = curl_request(f"{MCP_SERVER_URL}{endpoint}", method="POST", data=mcp_request)
        if response and response != "Not Found":
            print(f"   ✅ Working endpoint: {endpoint}")
            print(f"   Response: {response}")
            working_endpoint = endpoint
            break
    else:
        print("   ❌ No working endpoint found")
        return
    
    # Step 3: Test get_email tool
    print("\n[3] Testing get_email tool...")
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_email",
            "arguments": {
                "account_id": "12345",
                "jwt_token": token,
                "tenant_id": tenant_id
            }
        }
    }
    response = curl_request(f"{MCP_SERVER_URL}{working_endpoint}", method="POST", data=mcp_request)
    print(f"Response: {response}")
    
    # Step 4: Test change_email - Step 2 (request confirmation)
    print("\n[4] Testing change_email - Request confirmation...")
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "change_email",
            "arguments": {
                "account_id": "12345",
                "jwt_token": token,
                "tenant_id": tenant_id,
                "new_email": "newemail@example.com"
            }
        }
    }
    response = curl_request(f"{MCP_SERVER_URL}{working_endpoint}", method="POST", data=mcp_request)
    print(f"Response: {response}")
    
    # Step 5: Test change_email - Step 3 (confirmed)
    print("\n[5] Testing change_email - Confirmed...")
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "change_email",
            "arguments": {
                "account_id": "12345",
                "jwt_token": token,
                "tenant_id": tenant_id,
                "new_email": "newemail@example.com",
                "user_confirmation": "Y"
            }
        }
    }
    response = curl_request(f"{MCP_SERVER_URL}{working_endpoint}", method="POST", data=mcp_request)
    print(f"Response: {response}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")


if __name__ == "__main__":
    main()
