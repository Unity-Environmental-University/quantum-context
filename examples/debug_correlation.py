"""Debug correlation calculation"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from quantum_context import act_record
from quantum_context.core import _load_all_measurements, _compute_correlation, GRAPH_FILE

# Clear graph
if GRAPH_FILE.exists():
    GRAPH_FILE.unlink()

# Create test data
act_record("auth", "requires", "identity", confidence=0.7, confirm=True)
act_record("payment", "requires", "card", confidence=0.7, confirm=True)
act_record("auth", "uses", "database", confidence=0.5, confirm=True)
act_record("payment", "uses", "database", confidence=0.6, confirm=True)

# Load and check
measurements = _load_all_measurements()

print("Measurements:")
for m in measurements:
    print(f"  {m['subject']} {m['predicate']} {m['object']}")

print("\nSubjects as subjects:", set(m['subject'] for m in measurements))
print("Subjects as objects:", set(m['object'] for m in measurements))

print("\nTesting correlation(auth, payment):")
corr = _compute_correlation(measurements, "auth", "payment")
print(f"  Result: {corr:.3f}")
print(f"  Expected: ~0.14 (shared database only)")

print("\nAuth objects:", set(m['object'] for m in measurements if m['subject'] == 'auth'))
print("Payment objects:", set(m['object'] for m in measurements if m['subject'] == 'payment'))
print("Shared objects:", set(m['object'] for m in measurements if m['subject'] == 'auth') &
                        set(m['object'] for m in measurements if m['subject'] == 'payment'))
