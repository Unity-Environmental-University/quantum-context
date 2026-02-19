"""
Quantum context graph - observer-relative knowledge via wave interference.

Philosophy: The universe is a holographic projection from ℤ.
Any integer can be the origin. Divisibility = causality. Waves preserve structure.
"""

from quantum_context.core import (
    observe_context,
    compute_mismatch,
    analyze_dependencies,
    act_record,
)
from quantum_context.compare import compare_observers, detect_systematic_bias

__version__ = "0.3.0"

# Friction gradient encoded in export order
__all__ = [
    "observe_context",           # Low friction - read only (now with phase)
    "compare_observers",         # Low friction - read only (comparison)
    "compute_mismatch",          # Medium - expectation vs measurement
    "analyze_dependencies",      # Medium - compute patterns
    "detect_systematic_bias",    # Medium - analyze patterns
    "act_record",               # High - requires confirmation
]
