#!/bin/bash
# Quick install script for quantum-context

set -e

echo "🌊 Installing quantum-context..."
echo

# Install package
pip install -e ".[mcp]"

echo
echo "✅ quantum-context installed!"
echo

# Ask about MCP setup
read -p "Add quantum-context as an MCP server to Claude Desktop? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    echo "Run this command to add the MCP server:"
    echo
    echo "  claude mcp add quantum-context -- python3 $SCRIPT_DIR/mcp_server.py"
    echo
    echo "Or manually add to ~/.claude/settings.json:"
    echo
    echo "{"
    echo "  \"mcpServers\": {"
    echo "    \"quantum-context\": {"
    echo "      \"command\": \"python3\","
    echo "      \"args\": [\"$SCRIPT_DIR/mcp_server.py\"],"
    echo "      \"cwd\": \"$SCRIPT_DIR\""
    echo "    }"
    echo "  }"
    echo "}"
    echo
fi

echo "📖 Usage:"
echo "  Python: from quantum_context import observe_context, act_record"
echo "  MCP: Restart Claude Desktop after adding the server"
echo
echo "🌊 The universe is a holographic projection from ℤ."
