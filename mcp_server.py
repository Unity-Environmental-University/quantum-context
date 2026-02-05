#!/usr/bin/env python3
"""
Quantum Context MCP Server

Exposes quantum-context as MCP tools for Claude Desktop.
"""

import asyncio
import sys
from typing import Any

# Add quantum_context to path
sys.path.insert(0, ".")

from quantum_context import observe_context, analyze_dependencies, act_record

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


# Create server instance
server = Server("quantum-context")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available quantum context tools."""
    return [
        Tool(
            name="quantum_observe",
            description="Observe context about a subject (low friction - read only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject to observe (e.g., 'authentication', 'skill-starter')",
                    },
                    "observer": {
                        "type": "string",
                        "description": "Observer frame (default: 'claude')",
                        "default": "claude",
                    },
                },
                "required": ["subject"],
            },
        ),
        Tool(
            name="quantum_analyze",
            description="Analyze dependencies and relationships (medium friction)",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject to analyze dependencies for",
                    },
                },
                "required": ["subject"],
            },
        ),
        Tool(
            name="quantum_record",
            description="Record a measurement to the graph (high friction - requires confirmation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Subject of the measurement",
                    },
                    "predicate": {
                        "type": "string",
                        "description": "Relationship/predicate (e.g., 'requires', 'implements', 'status')",
                    },
                    "object": {
                        "type": "string",
                        "description": "Object of the measurement",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence level (0.0-1.0, capped at 0.7 without evidence)",
                        "default": 0.5,
                        "minimum": 0.0,
                        "maximum": 1.0,
                    },
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Evidence URLs/citations (required to exceed 0.7 confidence)",
                        "default": [],
                    },
                    "observer": {
                        "type": "string",
                        "description": "Observer making this measurement",
                        "default": "claude",
                    },
                },
                "required": ["subject", "predicate", "object"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""

    if name == "quantum_observe":
        subject = arguments["subject"]
        observer = arguments.get("observer", "claude")

        result = observe_context(subject, observer=observer)

        return [
            TextContent(
                type="text",
                text=f"Observed: {subject}\n"
                     f"Wave magnitude: {result.magnitude:.2f}\n"
                     f"Coefficients: {result.coefficients}\n"
                     f"Entity: {result.entity}",
            )
        ]

    elif name == "quantum_analyze":
        subject = arguments["subject"]

        result = analyze_dependencies(subject)

        deps_text = "\n".join(f"  - {dep} (conf: {conf})"
                             for dep, conf in result.shared_structure.items())

        return [
            TextContent(
                type="text",
                text=f"Dependencies for: {subject}\n\n"
                     f"Depends on:\n{deps_text or '  (none)'}\n\n"
                     f"Total relationships: {len(result.depends_on)}",
            )
        ]

    elif name == "quantum_record":
        subject = arguments["subject"]
        predicate = arguments["predicate"]
        obj = arguments["object"]
        confidence = arguments.get("confidence", 0.5)
        evidence = arguments.get("evidence", [])
        observer = arguments.get("observer", "claude")

        # MCP server auto-confirms (user approved via MCP)
        result = act_record(
            subject,
            predicate,
            obj,
            confidence=confidence,
            evidence=evidence,
            observer=observer,
            confirm=True,
        )

        return [
            TextContent(
                type="text",
                text=f"✅ Recorded: {subject} {predicate} {obj}\n"
                     f"Confidence: {result['measurement']['confidence']}\n"
                     f"Observer: {observer}\n"
                     f"Timestamp: {result['measurement']['timestamp']}",
            )
        ]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
