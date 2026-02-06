# Adding quantum-context to Claude

Two ways to use quantum-context with Claude: **MCP Server** (recommended) or **Skill**.

## Option 1: MCP Server (Recommended)

Best for Claude Desktop users. Provides three tools: `quantum_observe`, `quantum_analyze`, `quantum_record`.

### Setup

1. **Install with MCP support:**
   ```bash
   pip install quantum-context[mcp]
   ```

2. **Find the MCP server location:**
   ```bash
   python -c "import quantum_context; import os; print(os.path.dirname(quantum_context.__file__))"
   # Example output: /opt/miniconda3/lib/python3.13/site-packages/quantum_context
   ```

3. **Add to Claude Desktop settings** (`~/.claude/settings.json`):
   ```json
   {
     "mcpServers": {
       "quantum-context": {
         "command": "python3",
         "args": ["-m", "mcp.server", "quantum_context.mcp_server"],
         "env": {}
       }
     }
   }
   ```

   Or using the installed mcp_server.py directly:
   ```json
   {
     "mcpServers": {
       "quantum-context": {
         "command": "python3",
         "args": ["/path/from/step2/mcp_server.py"]
       }
     }
   }
   ```

4. **Restart Claude Desktop**

5. **Test it:**
   Ask Claude: "What quantum context tools do you have?"

   Should see: `quantum_observe`, `quantum_analyze`, `quantum_record`

### Usage via MCP

```
User: "What do we know about authentication?"
Claude: [Uses quantum_observe to check]

User: "Record that we completed the login feature"
Claude: [Uses quantum_record with confirmation]
```

## Option 2: Claude Skill

Best for Claude Code (CLI) users. More direct integration.

### Setup

1. **Install quantum-context:**
   ```bash
   pip install quantum-context
   ```

2. **Copy skill.md to Claude skills directory:**
   ```bash
   # Find your Claude skills directory
   # Usually ~/.claude/skills/

   cp skill.md ~/.claude/skills/quantum-context.md
   ```

3. **Restart Claude or reload skills**

### Usage as Skill

Claude will automatically use quantum-context functions when relevant:

```python
# Claude can now directly use:
from quantum_context import observe_context, analyze_dependencies, act_record

# And will follow the friction gradient:
# - observe = low friction (no confirmation)
# - analyze = medium friction
# - act_record = high friction (requires confirmation)
```

## Quick Start Examples

### Session Continuity

**Session 1 (Monday):**
```
User: "We're using React and Auth0 for this project"
Claude: [Records this via quantum_record]
```

**Session 2 (Wednesday):**
```
User: "Add authentication to the dashboard"
Claude: [Uses quantum_observe to retrieve: "Project uses React + Auth0"]
Claude: "I see you're using Auth0. I'll integrate with that..."
```

### Multi-Agent Coordination

**Agent A (Frontend):**
```python
act_record("api", "protocol", "graphql",
           observer="agent-frontend", confirm=True)
```

**Agent B (Backend):**
```python
context = observe_context("api")
# Sees: protocol = graphql (from agent-frontend)
# Builds GraphQL server instead of REST
```

## Verification

Test that it's working:

```
User: "Record that quantum-context is installed"
Claude: [Uses act_record]

User: "What do we know about quantum-context?"
Claude: [Uses observe_context]
# Should see: status = installed
```

## Troubleshooting

**MCP server not showing:**
- Check `~/.claude/settings.json` syntax (valid JSON)
- Verify Python path is correct (`which python3`)
- Restart Claude Desktop fully
- Check Claude Desktop logs

**Skill not loading:**
- Verify skill.md is in correct directory
- Check Python environment has quantum-context installed
- Try reloading skills in Claude

**Import errors:**
```bash
# Verify installation
pip show quantum-context

# Test import
python -c "from quantum_context import observe_context; print('OK')"
```

## Storage Location

All measurements stored in:
```
~/.quantum-context/graph.ndjson
```

Plain text, git-friendly, portable!

## Learn More

- Full API: `quantum-context --help`
- Theory: See README.md
- Examples: See examples/ directory
- Ethics: See RESPONSIBLE_USE.md

---

*Measure. Compress. Interfere. Understand.*
