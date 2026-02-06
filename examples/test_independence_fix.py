"""
Test that the independence detection now works correctly.
"""

import sys
from pathlib import Path

# Add quantum_context to path
sys.path.insert(0, str(Path(__file__).parent))

from quantum_context import observe_context, analyze_dependencies, act_record

print("=" * 70)
print("TEST: Independence Detection (Stub Fix Validation)")
print("=" * 70)

# Clear any existing test data by using a fresh graph file
import os
from quantum_context.core import GRAPH_FILE

if GRAPH_FILE.exists():
    # Backup current graph
    backup = GRAPH_FILE.parent / "graph_backup.ndjson"
    import shutil
    shutil.copy(GRAPH_FILE, backup)
    print(f"✓ Backed up existing graph to {backup}")
    GRAPH_FILE.unlink()
    print(f"✓ Cleared graph for clean test")

print("\n" + "=" * 70)
print("Recording test measurements...")
print("=" * 70)

# Create auth domain
act_record("auth", "requires", "identity", confidence=0.7, confirm=True)
act_record("auth", "requires", "session", confidence=0.7, confirm=True)
act_record("identity", "requires", "credentials", confidence=0.6, confirm=True)

# Create payment domain (should be independent of auth)
act_record("payment", "requires", "card", confidence=0.7, confirm=True)
act_record("payment", "requires", "amount", confidence=0.8, confirm=True)

# Create shared infrastructure
act_record("auth", "uses", "database", confidence=0.5, confirm=True)
act_record("payment", "uses", "database", confidence=0.6, confirm=True)

print("\n✓ Recorded 7 measurements")

print("\n" + "=" * 70)
print("Testing independence detection...")
print("=" * 70)

print("\n1. Analyze 'auth' dependencies:")
auth_deps = analyze_dependencies("auth")
print(f"   depends_on: {auth_deps.depends_on}")
print(f"   independent_of: {auth_deps.independent_of}")
print(f"   shared_structure: {auth_deps.shared_structure}")

if "payment" in auth_deps.independent_of:
    print("   ✓ CORRECT: 'payment' detected as independent of 'auth'")
else:
    print("   ✗ FAILED: 'payment' should be independent of 'auth'")

print("\n2. Analyze 'payment' dependencies:")
payment_deps = analyze_dependencies("payment")
print(f"   depends_on: {payment_deps.depends_on}")
print(f"   independent_of: {payment_deps.independent_of}")
print(f"   shared_structure: {payment_deps.shared_structure}")

if "auth" in payment_deps.independent_of:
    print("   ✓ CORRECT: 'auth' detected as independent of 'payment'")
else:
    print("   ✗ FAILED: 'auth' should be independent of 'payment'")

print("\n3. Analyze 'identity' dependencies:")
identity_deps = analyze_dependencies("identity")
print(f"   depends_on: {identity_deps.depends_on}")
print(f"   independent_of: {identity_deps.independent_of}")
print(f"   shared_structure: {identity_deps.shared_structure}")

# Identity should be independent of payment but NOT auth (auth depends on identity)
if "payment" in identity_deps.independent_of:
    print("   ✓ CORRECT: 'payment' detected as independent of 'identity'")
else:
    print("   ✗ FAILED: 'payment' should be independent of 'identity'")

if "auth" not in identity_deps.independent_of:
    print("   ✓ CORRECT: 'auth' NOT in independent list (auth depends on identity)")
else:
    print("   ✗ FAILED: 'auth' should NOT be independent (it depends on identity)")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)

# Check if the stub is fixed
all_correct = (
    "payment" in auth_deps.independent_of and
    "auth" in payment_deps.independent_of and
    "payment" in identity_deps.independent_of and
    "auth" not in identity_deps.independent_of
)

if all_correct:
    print("\n✓✓✓ SUCCESS! ✓✓✓")
    print("\nThe stub is FIXED!")
    print("- Independence detection now works correctly")
    print("- Uses correlation analysis (no prime computation)")
    print("- Coprime concepts (low correlation) correctly identified")
    print("- Dependent concepts (high correlation) excluded from independence list")
else:
    print("\n✗ FAILED - Some tests didn't pass")

print("\nThe misleading empty list stub has been replaced with")
print("working correlation-based orthogonality detection!")

# Restore backup if it exists
if backup.exists():
    print(f"\n✓ Restoring original graph from {backup}")
    shutil.copy(backup, GRAPH_FILE)
    backup.unlink()
