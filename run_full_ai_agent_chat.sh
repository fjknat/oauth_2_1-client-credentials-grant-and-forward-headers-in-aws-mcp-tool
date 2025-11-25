#!/bin/bash

# Define paths
ROOT_DIR=$(pwd)
API_DIR="$ROOT_DIR/packages/api-server"
MCP_SERVER_DIR="$ROOT_DIR/packages/mcp-server"
AI_AGENT_DIR="$ROOT_DIR/packages/ai-agent-chatbox"

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
echo "🚀 Starting AI Agent Chat Environment"
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

# 3. Run AI Agent Chatbox
echo ""
echo "3️⃣  Starting AI Agent Chatbox..."
echo "--------------------------------------------------"
cd "$AI_AGENT_DIR"

# Ensure venv is activated (it should be from step 2, but good to be sure if logic changes)
if [ -f "$ROOT_DIR/.venv-4/Scripts/activate" ]; then
    source "$ROOT_DIR/.venv-4/Scripts/activate"
elif [ -f "$ROOT_DIR/.venv-4/bin/activate" ]; then
    source "$ROOT_DIR/.venv-4/bin/activate"
fi

# Check if requirements need to be installed (simple check)
# We'll just run pip install -r requirements.txt quietly to ensure deps are there
# This might slow down startup slightly but ensures it works
echo "   - Checking dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Clean up sessions
echo "   - Cleaning up old sessions..."
rm -rf sessions
mkdir -p sessions

export PYTHONIOENCODING=utf-8
python chatbox.py

# When client exits, the trap will trigger cleanup
