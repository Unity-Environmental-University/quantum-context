# MCP Server Setup for Claude Desktop

## Install MCP SDK

```bash
pip install mcp
```

## Add to Claude Desktop

Add this to your `~/.claude/settings.json` (or Claude Desktop settings):

```json
{
  "mcpServers": {
    "quantum-context": {
      "command": "python3",
      "args": ["/Users/hallie/Documents/repos/unity/claude-skills/quantum-context/mcp_server.py"],
      "cwd": "/Users/hallie/Documents/repos/unity/claude-skills/quantum-context"
    }
  }
}
```

Or use the Claude CLI:

```bash
claude mcp add quantum-context -- python3 /Users/hallie/Documents/repos/unity/claude-skills/quantum-context/mcp_server.py
```

## Restart Claude Desktop

After adding the MCP server, restart Claude Desktop to load it.

## Usage

Once loaded, you'll have three tools available:

### `quantum_observe`
Read measurements about a subject (low friction).

```
Use quantum_observe to check what we know about "authentication"
```

### `quantum_analyze`
Analyze dependencies and relationships (medium friction).

```
Use quantum_analyze to see what "quantum-context-skill" depends on
```

### `quantum_record`
Record a measurement (high friction - but MCP handles confirmation).

```
Use quantum_record to save: subject="my-project", predicate="status", object="complete", confidence=0.7
```

## Verify It's Working

After restart, Claude Desktop should show "quantum-context" in the MCP servers list.

Test with:
```
What quantum context tools do you have available?
```

Claude should list: quantum_observe, quantum_analyze, quantum_record

## Philosophy

The MCP server wraps the quantum-context library, maintaining the friction gradient:
- **observe**: No barriers (read measurements)
- **analyze**: Computation cost (find patterns)
- **record**: Confirmation via MCP (modify shared reality)

Epistemic humility is enforced: 0.7 confidence ceiling without evidence.

---

*Measure. Compress. Interfere. Understand.*
