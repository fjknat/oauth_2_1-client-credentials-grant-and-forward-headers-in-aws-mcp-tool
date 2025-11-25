#!/bin/bash

# Define paths
ROOT_DIR=$(pwd)
API_DIR="$ROOT_DIR/packages/api-server"
MCP_SERVER_DIR="$ROOT_DIR/packages/mcp-server"
MCP_CLIENT_DIR="$ROOT_DIR/packages/mcp-client"

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    if [ -n "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo "   - API Server stopped"
    fi
    if [ -n "$MCP_SERVER_PID" ]; then
        kill $MCP_SERVER_PID 2>/dev/null
        echo "   - MCP Server stopped"
    fi
    exit
}

# Trap SIGINT (Ctrl+C) and EXIT
trap cleanup SIGINT EXIT

echo "=================================================="
echo "🚀 Starting Full MCP Demo Environment"
echo "=================================================="

# 1. Run API Server
echo ""
echo "1️⃣  Starting API Server..."
cd "$API_DIR"
# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    echo "   - Installing API dependencies..."
    npm install > /dev/null 2>&1
fi
npm start > /dev/null 2>&1 &
API_PID=$!
echo "   - API Server running (PID: $API_PID)"
sleep 3 # Give it a moment to start

# 2. Run MCP Server
echo ""
echo "2️⃣  Starting MCP Server..."
cd "$MCP_SERVER_DIR"
# Activate virtual environment if it exists
if [ -f "$ROOT_DIR/.venv-4/Scripts/activate" ]; then
    source "$ROOT_DIR/.venv-4/Scripts/activate"
elif [ -f "$ROOT_DIR/.venv-4/bin/activate" ]; then
    source "$ROOT_DIR/.venv-4/bin/activate"
fi

python server.py > /dev/null 2>&1 &
MCP_SERVER_PID=$!
echo "   - MCP Server running (PID: $MCP_SERVER_PID)"
sleep 3 # Give it a moment to start

# 3. Run MCP Client
echo ""
echo "3️⃣  Starting MCP Client..."
echo "--------------------------------------------------"
cd "$MCP_CLIENT_DIR"
python client.py

# When client exits, the trap will trigger cleanup
