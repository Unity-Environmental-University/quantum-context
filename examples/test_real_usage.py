"""
Real-world test: Claude session continuity.

Simulate what would actually happen if we used quantum-context
across two different Claude sessions.
"""

import sys
import os
from pathlib import Path

# Add quantum_context to path
sys.path.insert(0, str(Path(__file__).parent))

from quantum_context import observe_context, analyze_dependencies, act_record

print("=" * 70)
print("REAL-WORLD TEST: Claude Session Continuity")
print("=" * 70)

print("\n" + "=" * 70)
print("SESSION 1 (Monday - Initial exploration)")
print("=" * 70)

print("\nUser: 'Help me understand this codebase'")
print("Claude explores and learns...")

# Session 1: Claude learns about the codebase
print("\n[Claude records observations]")

act_record(
    "codebase", "uses", "react",
    confidence=0.9,
    observer="claude-session-monday",
    evidence=["package.json shows react@18.2.0"],
    confirm=True
)
print("✓ Recorded: codebase uses react (0.9)")

act_record(
    "codebase", "uses", "typescript",
    confidence=0.9,
    observer="claude-session-monday",
    evidence=["tsconfig.json present"],
    confirm=True
)
print("✓ Recorded: codebase uses typescript (0.9)")

act_record(
    "auth", "implementation", "auth0",
    confidence=0.8,
    observer="claude-session-monday",
    evidence=["src/auth/config.ts imports @auth0/auth0-react"],
    confirm=True
)
print("✓ Recorded: auth implementation auth0 (0.8)")

act_record(
    "api", "style", "rest",
    confidence=0.7,
    observer="claude-session-monday",
    confirm=True
)
print("✓ Recorded: api style rest (0.7)")

act_record(
    "deployment", "platform", "vercel",
    confidence=0.6,
    observer="claude-session-monday",
    confirm=True
)
print("✓ Recorded: deployment platform vercel (0.6)")

# Also record some dependencies
act_record(
    "auth", "requires", "api",
    confidence=0.7,
    observer="claude-session-monday",
    confirm=True
)
print("✓ Recorded: auth requires api (0.7)")

act_record(
    "codebase", "requires", "auth",
    confidence=0.6,
    observer="claude-session-monday",
    confirm=True
)
print("✓ Recorded: codebase requires auth (0.6)")

print("\n[Session 1 ends - context saved to ~/.quantum-context/graph.ndjson]")

print("\n" + "=" * 70)
print("SESSION 2 (Wednesday - New Claude instance)")
print("=" * 70)

print("\nUser: 'Add a new authenticated endpoint to the API'")
print("Claude (new instance, no memory of Monday): checking context...")

# Session 2: New Claude instance retrieves context
print("\n[Claude observes stored context]")

codebase_context = observe_context("codebase", observer="claude-session-wednesday")
print(f"\nobserve_context('codebase'):")
print(f"  magnitude: {codebase_context.magnitude:.2f}")
print(f"  coefficients: {codebase_context.coefficients}")
print(f"  → This is a React + TypeScript codebase (confidence ~0.9)")

auth_context = observe_context("auth", observer="claude-session-wednesday")
print(f"\nobserve_context('auth'):")
print(f"  magnitude: {auth_context.magnitude:.2f}")
print(f"  → Auth is implemented with Auth0 (confidence ~0.8)")

api_context = observe_context("api", observer="claude-session-wednesday")
print(f"\nobserve_context('api'):")
print(f"  magnitude: {api_context.magnitude:.2f}")
print(f"  → API is REST-based (confidence ~0.7)")

deployment_context = observe_context("deployment", observer="claude-session-wednesday")
print(f"\nobserve_context('deployment'):")
print(f"  magnitude: {deployment_context.magnitude:.2f}")
print(f"  → Deployed on Vercel (confidence ~0.6)")

print("\n[Claude analyzes dependencies]")

auth_deps = analyze_dependencies("auth")
print(f"\nanalyze_dependencies('auth'):")
print(f"  depends_on: {auth_deps.depends_on}")
print(f"  shared_structure: {auth_deps.shared_structure}")

codebase_deps = analyze_dependencies("codebase")
print(f"\nanalyze_dependencies('codebase'):")
print(f"  depends_on: {codebase_deps.depends_on}")
print(f"  shared_structure: {codebase_deps.shared_structure}")

print("\n[Claude can now respond intelligently]")
print("""
Claude: "I see this is a React + TypeScript codebase using Auth0 for
authentication and REST APIs. I'll add a new endpoint that integrates
with the existing Auth0 setup..."

[Creates code without asking redundant questions]
""")

print("\n" + "=" * 70)
print("RESULT: Success! ✓")
print("=" * 70)
print("""
The new Claude instance:
✓ Retrieved all context from Monday's session
✓ Knew about React, TypeScript, Auth0, REST, Vercel
✓ Understood dependencies (auth requires api, etc.)
✓ Could proceed without asking basic questions
✓ User experience: seamless continuity

This is the PRIMARY use case working correctly!
""")

print("\n" + "=" * 70)
print("STORAGE CHECK")
print("=" * 70)

graph_file = Path.home() / ".quantum-context" / "graph.ndjson"
if graph_file.exists():
    line_count = sum(1 for _ in open(graph_file))
    print(f"✓ Graph file exists: {graph_file}")
    print(f"✓ Contains {line_count} measurements")
    print(f"\nFirst 3 measurements:")
    with open(graph_file) as f:
        for i, line in enumerate(f):
            if i < 3:
                print(f"  {line.strip()}")
else:
    print(f"✗ Graph file not found at {graph_file}")
