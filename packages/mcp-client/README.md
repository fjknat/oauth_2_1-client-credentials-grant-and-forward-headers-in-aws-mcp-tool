# MCP Client Chatbox CLI

A Python-based CLI application that acts as a client for the Model Context Protocol (MCP). It uses the `FastMCP` library to connect to an MCP server via Streamable HTTP, supporting secure authentication and tool execution.

## Features

- 🚀 **FastMCP Integration**: Uses `FastMCP` client with `StreamableHttpTransport` for robust communication.
- 🔐 **Secure Authentication**: 
  - Fetches JWT tokens from the API server.
  - Injects `X-JWT-TOKEN` and `X-TENANT-ID` headers into all MCP requests.
- 🛠️ **Tool Discovery**: Automatically lists available tools, resources, and prompts upon connection.
- 📊 **Rich Interactions**: Supports text-based tools (`get_email`, `change_email`) and binary resources (`get_chart` displays images).
- 🤝 **Human-in-the-Loop**: Handles client-side elicitation for confirmation workflows.

## Installation

1. Navigate to the client directory:
   ```bash
   cd packages/mcp-client
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Prerequisites
Ensure the backend services are running:
- **API Server**: `http://localhost:3006`
- **MCP Server**: `http://localhost:3005`

### 2. Run the Client
```bash
python client.py
```

### 3. Interactive Flow
1. **Startup**: The client will print a logo.
2. **Auth Setup**:
   - **JWT Token**: You will be asked `🔑 Do you want to get JWT token? (y/n)`. Type `y` to fetch a fresh token from the API server.
   - **Tenant ID**: You will be asked to enter a tenant ID. Default/Test value is `test123`.
3. **Connection**: The client connects to `http://127.0.0.1:3005/mcp` using the provided credentials.
4. **Discovery**: It lists all available tools and resources.

### 4. Commands
Once in the chat loop, you can use the following commands:

| Command | Alias | Description |
|---------|-------|-------------|
| `get_email` | `g` | Fetch email for a specific Account ID. |
| `change_email` | `c` | Initiate the email change workflow (requires confirmation). |
| `get_chart` | `gc` | Fetch and display a chart image. |
| `exit` | | Close the application. |

## Configuration

The client is configured via constants in `client.py`:
- `MCP_SERVER_URL`: `http://127.0.0.1:3005/mcp`

## Project Structure

```
mcp-client/
├── client.py           # Main CLI application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```
