"""Figure out what threshold makes sense"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from quantum_context import act_record
from quantum_context.core import _load_all_measurements, _compute_correlation, GRAPH_FILE

# Clear and create test data
if GRAPH_FILE.exists():
    GRAPH_FILE.unlink()

act_record("auth", "requires", "identity", confidence=0.7, observer="alice", confirm=True)
act_record("auth", "requires", "session", confidence=0.7, observer="alice", confirm=True)
act_record("payment", "requires", "card", confidence=0.7, observer="alice", confirm=True)
act_record("payment", "requires", "amount", confidence=0.7, observer="alice", confirm=True)
act_record("auth", "uses", "database", confidence=0.5, observer="alice", confirm=True)
act_record("payment", "uses", "database", confidence=0.6, observer="alice", confirm=True)

measurements = _load_all_measurements()
subjects = list(set(m['subject'] for m in measurements))

print("=" * 70)
print("CORRELATION MATRIX")
print("=" * 70)
print(f"\n{'':12s}", end='')
for s in subjects:
    print(f"{s:12s}", end='')
print()

for s1 in subjects:
    print(f"{s1:12s}", end='')
    for s2 in subjects:
        if s1 == s2:
            corr = 1.0
        else:
            corr = _compute_correlation(measurements, s1, s2)
        print(f"{corr:12.3f}", end='')
    print()

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)

auth_payment = _compute_correlation(measurements, "auth", "payment")
print(f"\nCorrelation(auth, payment) = {auth_payment:.3f}")
print(f"  Shared: database (weak 'uses' relationship)")
print(f"  Same observer: alice")
print(f"  Should be: INDEPENDENT (different domains)")

print(f"\nProposed thresholds:")
print(f"  < 0.3: Independent (weak infrastructure sharing doesn't count)")
print(f"  0.3-0.6: Moderate relationship")
print(f"  > 0.6: Strong dependency")

print(f"\nWith threshold=0.3:")
if auth_payment < 0.3:
    print(f"  ✓ auth and payment would be independent")
else:
    print(f"  ✗ auth and payment still not independent ({auth_payment:.3f} >= 0.3)")

print(f"\nWith threshold=0.5:")
if auth_payment < 0.5:
    print(f"  ✓ auth and payment would be independent")
else:
    print(f"  ✗ auth and payment still not independent ({auth_payment:.3f} >= 0.5)")

print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print("""
The issue: Same observer contributes 0.3 to correlation, and weak
infrastructure sharing adds 0.1, giving 0.4 total.

Options:
1. Raise threshold to 0.5 (pragmatic)
2. Reduce observer weight from 0.3 to 0.1 (principled)
3. Only count observer overlap if there's structural overlap (most principled)

Option 3 is best: Observer frame should boost existing correlation,
not create correlation where there's no structural relationship.
""")
