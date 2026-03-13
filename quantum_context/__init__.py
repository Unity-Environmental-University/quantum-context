"""
Quantum context graph - observer-relative knowledge via wave interference.

Philosophy: The universe is a holographic projection from ℤ.
Any integer can be the origin. Divisibility = causality. Waves preserve structure.
Words have gravity. Everything has a true name, but its true name is different to each other thing.
"""

from quantum_context.core import observe_context, analyze_dependencies, act_record
from quantum_context.compare import compare_observers, detect_systematic_bias
from quantum_context.wave import compute_wave, interference, compute_phase, compute_frequency

__version__ = "0.3.0"

# Friction gradient encoded in export order
__all__ = [
    # Low friction - observe
    "observe_context",           # Read context (now with phase)
    "compare_observers",         # Compare frames
    "compute_wave",              # Construct ψ directly
    "interference",              # |ψ(A)·ψ(B)|²
    "compute_phase",             # Temporal phase
    "compute_frequency",         # Natural frequency
    # Medium friction - analyze
    "analyze_dependencies",      # Dependency structure
    "detect_systematic_bias",    # Observer bias
    # High friction - act
    "act_record",               # Modify shared reality
]
