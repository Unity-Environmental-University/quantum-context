"""
Test: Does wave interference preserve divisibility structure?

Setup:
  - Two related concepts (auth, session) measured at similar times
    → should share phase → constructive interference
  - Two independent concepts (auth, payment) measured at different times
    → should diverge in phase → less constructive interference
  - Two concepts with shared infrastructure but no structural dependency
    → should show weak interference despite shared observer

The question: does |ψ(A)·ψ(B)|² track with correlation/divisibility?

If yes: phase is doing real work. The wave function isn't just a metaphor.
If no: phase is decorative and we should be honest about that.
"""

import sys
import math
from datetime import datetime, timedelta

# Add parent to path for imports
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from quantum_context.wave import compute_wave, interference, compute_phase, compute_frequency
from quantum_context.core import _compute_correlation


def make_measurements():
    """
    Create a measurement graph with known structure.

    Causal structure (what divides what):
      identity ← auth ← session (auth requires identity, session requires auth)
      card ← payment (payment requires card)
      auth uses database
      payment uses database

    Temporal structure:
      auth/identity/session measured in a burst (9:00-9:05)
      payment/card measured in a different burst (14:00-14:05)
      database mentioned by both but at different times
    """
    base = datetime(2026, 2, 16, 9, 0, 0)

    measurements = [
        # Auth domain - morning burst
        {"subject": "auth", "predicate": "requires", "object": "identity",
         "confidence": 0.7, "observer": "alice", "timestamp": (base + timedelta(minutes=0)).isoformat()},
        {"subject": "auth", "predicate": "requires", "object": "session",
         "confidence": 0.6, "observer": "alice", "timestamp": (base + timedelta(minutes=2)).isoformat()},
        {"subject": "session", "predicate": "requires", "object": "auth",
         "confidence": 0.7, "observer": "alice", "timestamp": (base + timedelta(minutes=3)).isoformat()},
        {"subject": "auth", "predicate": "uses", "object": "database",
         "confidence": 0.5, "observer": "alice", "timestamp": (base + timedelta(minutes=5)).isoformat()},
        {"subject": "identity", "predicate": "requires", "object": "credentials",
         "confidence": 0.6, "observer": "alice", "timestamp": (base + timedelta(minutes=1)).isoformat()},

        # Payment domain - afternoon burst (5 hours later)
        {"subject": "payment", "predicate": "requires", "object": "card",
         "confidence": 0.7, "observer": "bob", "timestamp": (base + timedelta(hours=5, minutes=0)).isoformat()},
        {"subject": "payment", "predicate": "requires", "object": "amount",
         "confidence": 0.7, "observer": "bob", "timestamp": (base + timedelta(hours=5, minutes=2)).isoformat()},
        {"subject": "payment", "predicate": "uses", "object": "database",
         "confidence": 0.6, "observer": "bob", "timestamp": (base + timedelta(hours=5, minutes=5)).isoformat()},
        {"subject": "card", "predicate": "requires", "object": "number",
         "confidence": 0.5, "observer": "bob", "timestamp": (base + timedelta(hours=5, minutes=1)).isoformat()},

        # A concept measured by both observers at different times
        {"subject": "database", "predicate": "requires", "object": "connection",
         "confidence": 0.6, "observer": "alice", "timestamp": (base + timedelta(minutes=10)).isoformat()},
        {"subject": "database", "predicate": "requires", "object": "connection",
         "confidence": 0.6, "observer": "bob", "timestamp": (base + timedelta(hours=5, minutes=10)).isoformat()},
    ]

    return measurements


def main():
    measurements = make_measurements()
    ref_time = datetime(2026, 2, 16, 12, 0, 0).isoformat()  # Noon as reference

    print("=" * 70)
    print("WAVE INTERFERENCE TEST")
    print("Does |ψ(A)·ψ(B)|² preserve divisibility structure?")
    print("=" * 70)

    # Compute wave functions for each concept
    concepts = ["auth", "session", "identity", "payment", "card", "database"]
    waves = {}

    print("\n--- Wave Functions ---\n")
    for c in concepts:
        w = compute_wave(c, measurements, reference_time=ref_time)
        waves[c] = w
        print(f"ψ({c:12s}) = {w.magnitude:.3f} · e^(i·{w.phase:.3f})")
        print(f"  {'frequency':>12s} = {getattr(w, 'frequency', 0):.4f} measurements/hour")
        print(f"  {'predicates':>12s} = {getattr(w, 'predicates', [])}")
        print()

    # Test interference between pairs
    test_pairs = [
        # Related concepts (should be constructive)
        ("auth", "session", "RELATED (auth↔session, measured together)"),
        ("auth", "identity", "RELATED (auth requires identity, measured together)"),
        ("payment", "card", "RELATED (payment requires card, measured together)"),

        # Independent concepts (should be destructive or weak)
        ("auth", "payment", "INDEPENDENT (different domains, different times)"),
        ("identity", "card", "INDEPENDENT (no shared structure)"),
        ("session", "amount", "INDEPENDENT (no relationship)"),

        # Shared infrastructure (should be weak despite shared object)
        ("auth", "database", "INFRASTRUCTURE (auth uses database)"),
        ("payment", "database", "INFRASTRUCTURE (payment uses database)"),
    ]

    print("\n--- Interference Patterns ---\n")
    print(f"{'Pair':<25s} {'|ψ·ψ|²':>8s} {'Δφ':>8s} {'cos²':>8s} {'Type':>14s}  Expectation")
    print("-" * 90)

    results = []
    for a, b, description in test_pairs:
        if a not in waves or b not in waves:
            # concept might not have subject-level measurements
            w_a = compute_wave(a, measurements, reference_time=ref_time)
            w_b = compute_wave(b, measurements, reference_time=ref_time)
        else:
            w_a, w_b = waves[a], waves[b]

        if w_a.magnitude == 0 or w_b.magnitude == 0:
            print(f"{a+'×'+b:<25s} {'N/A':>8s}  (no measurements as subject)")
            continue

        result = interference(w_a, w_b, measurements=measurements)

        # Also compute correlation for comparison
        corr = _compute_correlation(measurements, a, b)

        print(
            f"{a+'×'+b:<25s} "
            f"{result['intensity']:>8.4f} "
            f"{result['phase_diff']:>8.3f} "
            f"{result['cos_term']:>8.3f} "
            f"{result['resonance']:>14s}  "
            f"{description}"
        )
        results.append((a, b, result, corr, description))

    # Analysis
    print("\n\n--- Correlation vs Interference ---\n")
    print(f"{'Pair':<25s} {'Correlation':>12s} {'Interference':>12s} {'Agreement?':>12s}")
    print("-" * 65)

    agreements = 0
    total = 0

    for a, b, result, corr, desc in results:
        # Do they agree on related vs independent?
        corr_says_related = corr >= 0.3
        interference_says_related = result["resonance"] == "constructive"

        agrees = corr_says_related == interference_says_related
        if agrees:
            agreements += 1
        total += 1

        print(
            f"{a+'×'+b:<25s} "
            f"{corr:>12.3f} "
            f"{result['intensity']:>12.4f} "
            f"{'✓ yes' if agrees else '✗ NO':>12s}  "
            f"{'(related)' if corr_says_related else '(independent)'}"
        )

    print(f"\nAgreement: {agreements}/{total} ({100*agreements/total:.0f}%)")

    print("\n\n--- Verdict ---\n")
    if agreements == total:
        print("✓ PERFECT AGREEMENT")
        print("  Interference patterns preserve the same structure as correlation.")
        print("  Phase is doing real work. The wave function isn't decorative.")
        print("  Concepts measured together resonate. Concepts measured apart don't.")
        print()
        print("  The standing wave on ℤ lands here.")
    elif agreements / total > 0.75:
        print("◐ MOSTLY AGREES")
        print(f"  {agreements}/{total} pairs agree between correlation and interference.")
        print("  Phase captures temporal structure that correlation misses (or vice versa).")
        print("  The disagreements are interesting — they might reveal new structure.")
    else:
        print("✗ DISAGREEMENT")
        print(f"  Only {agreements}/{total} pairs agree.")
        print("  Phase and correlation are measuring different things.")
        print("  This is honest. Back to the drawing board on phase computation.")


if __name__ == "__main__":
    main()
