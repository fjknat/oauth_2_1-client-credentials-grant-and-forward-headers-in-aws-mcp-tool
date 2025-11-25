# MCP Server - Email & Chart Management

A FastMCP-based server providing email management operations and chart visualization tools. It features secure JWT authentication via HTTP headers and supports human-in-the-loop workflows.

## Features

- 🚀 **FastMCP**: Built with the modern FastMCP framework.
- 🔐 **Header-Based Auth**: Secure authentication using `x-jwt-token` and `x-tenant-id` headers (handled via Middleware).
- 📧 **Email Management**: Tools to retrieve and update user emails with validation.
- 📊 **Visualizations**: Tools to generate and retrieve chart images.
- 🤝 **Human-in-the-Loop**: Interactive workflow for sensitive operations like email changes.

## Installation

```bash
cd packages/mcp-server
pip install -r requirements.txt
```

## Run Server

```bash
python server.py
```

Server will start on `http://localhost:3005` with SSE transport.

## Authentication

This server uses **Middleware** to handle authentication. You do **NOT** pass credentials as arguments to the tools. Instead, the client must inject them into the request headers:

- `x-jwt-token`: A valid JWT token (obtained from the API Server).
- `x-tenant-id`: The tenant identifier (must be `test123`).

## MCP Tools

### 1. `get_email`
Retrieve the email address for a specific account.

- **Arguments:**
  - `account_id` (str): The 5-10 digit account ID.

### 2. `change_email`
Initiate a secure, multi-step process to change a user's email. This tool supports a Human-in-the-Loop workflow.

- **Arguments:**
  - `account_id` (str): The 5-10 digit account ID.
  - `new_email` (str, optional): The new email address.
  - `user_confirmation` (str, optional): 'Y' to confirm the change.

**Workflow:**
1.  **Request**: Call with just `account_id`. The tool returns a pending status asking for `new_email`.
2.  **Confirmation**: Call with `account_id` and `new_email`. The tool returns a pending status asking for `user_confirmation`.
3.  **Execution**: Call with `account_id`, `new_email`, and `user_confirmation='Y'`. The tool executes the change via the backend API.

### 3. `get_chart`
Returns a single sample chart image.

- **Returns**: An `Image` object (embedded resource).

### 4. `get_multiple_charts`
Returns a list of sample chart images.

- **Returns**: A list of `Image` objects.

## Configuration

The server is configured via variables in `server.py`:

- **PORT**: `3005`
- **API_BASE_URL**: `http://localhost:3006` (The backend API)
- **JWT_SECRET**: `your-secret-key` (Must match the API Server's secret)

## Testing Flow

1.  **Start the API Server** (Port 3006):
    ```bash
    cd packages/api-server && npm start
    ```
2.  **Start the MCP Server** (Port 3005):
    ```bash
    cd packages/mcp-server && python server.py
    ```
3.  **Get a Token**:
    ```bash
    curl http://localhost:3006/generate-token
    ```
4.  **Connect a Client**:
    Configure your MCP client (like the AI Agent Chatbox) to connect to `http://localhost:3005/mcp` and ensure it sends the required auth headers.
