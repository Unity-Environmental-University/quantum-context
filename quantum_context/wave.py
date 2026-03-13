"""
Wave mechanics for quantum context.

Magnitude = multiplicative structure (divisibility, GCD, confidence).
Phase = additive structure (temporal proximity, resonance, beats).
Interference = |ψ(A)·ψ(B)|² = how strongly two concepts resonate NOW.

The standing wave on ℤ: primes are fundamental frequencies.
Composite numbers are interference patterns.
The wave only lands at integer values.
"""

import math
import logging
from datetime import datetime
from typing import Optional

from quantum_context.models import WaveAmplitude

logger = logging.getLogger(__name__)


# =============================================================================
# Phase computation
# =============================================================================


def compute_phase(measurements: list[dict], reference_time: Optional[str] = None) -> float:
    """
    Compute phase of a concept from the temporal distribution of its measurements.

    Phase = where this concept sits in its oscillation cycle.

    Each measurement has a timestamp. The phase is derived from the
    temporal centroid of measurements relative to a reference time,
    mapped onto [0, 2π).

    If two concepts were measured at the same time, their phases align
    → constructive interference. If measured at different times, phases
    diverge → the interference pattern encodes temporal distance.

    This is the additive structure that magnitude alone misses.
    """
    if not measurements:
        return 0.0

    ref = _parse_time(reference_time) if reference_time else datetime.now()

    # Temporal offsets in hours from reference, weighted by confidence
    weighted_offsets = []
    total_weight = 0.0

    for m in measurements:
        try:
            t = _parse_time(m["timestamp"])
            offset_hours = (t - ref).total_seconds() / 3600.0
            weight = m.get("confidence", 0.5)
            weighted_offsets.append(offset_hours * weight)
            total_weight += weight
        except (KeyError, ValueError):
            continue

    if total_weight == 0:
        return 0.0

    # Temporal centroid (confidence-weighted average time offset)
    centroid = sum(weighted_offsets) / total_weight

    # Map to phase [0, 2π) using a natural period
    # The period is the temporal spread of measurements — each concept
    # has its own natural frequency based on how often it gets measured.
    # Concepts measured in bursts have high frequency (short period).
    # Concepts measured slowly have low frequency (long period).
    timestamps = []
    for m in measurements:
        try:
            timestamps.append(_parse_time(m["timestamp"]))
        except (KeyError, ValueError):
            continue

    if len(timestamps) < 2:
        # Single measurement: phase is just the offset mapped to [0, 2π)
        # Use a 24-hour natural period (one rotation per day)
        phase = (centroid / 24.0) * 2 * math.pi
        return phase % (2 * math.pi)

    # Natural period = temporal spread of this concept's measurements
    offsets = [(t - ref).total_seconds() / 3600.0 for t in timestamps]
    spread = max(offsets) - min(offsets)

    if spread < 0.001:  # All measurements at same time
        return 0.0

    # Phase = where the centroid sits within one period
    phase = ((centroid - min(offsets)) / spread) * 2 * math.pi

    return phase % (2 * math.pi)


def compute_frequency(measurements: list[dict]) -> float:
    """
    Natural frequency of a concept = how often it gets measured.

    High frequency = actively evolving concept (many measurements, close together)
    Low frequency = stable concept (few measurements, spread out)

    Returns measurements per hour.
    """
    if len(measurements) < 2:
        return 0.0

    timestamps = []
    for m in measurements:
        try:
            timestamps.append(_parse_time(m["timestamp"]))
        except (KeyError, ValueError):
            continue

    if len(timestamps) < 2:
        return 0.0

    timestamps.sort()
    span_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600.0

    if span_hours < 0.001:
        return float("inf")  # All at once = infinite frequency = impulse

    return (len(timestamps) - 1) / span_hours


# =============================================================================
# Interference
# =============================================================================


def interference(
    psi_a: WaveAmplitude,
    psi_b: WaveAmplitude,
    measurements: list[dict] | None = None,
) -> dict:
    """
    Compute interference between two wave functions.

    |ψ(A)·ψ(B)|² = magnitude_a · magnitude_b · cos²(Δphase/2)

    If measurements are provided, phase difference is computed from
    temporal co-occurrence — how close in time were A and B measured?
    This is the physical quantity. Things observed together resonate.
    Things observed apart don't.

    Without measurements, falls back to the stored phase values.

    Returns:
        amplitude: the raw interference amplitude
        intensity: |amplitude|² (the observable)
        phase_diff: Δphase between the two
        resonance: qualitative label

    Constructive: phases aligned → intensity approaches product of magnitudes
    Destructive: phases opposed → intensity approaches zero
    Partial: somewhere in between

    This is the Born rule. The probability of finding A and B
    in the same measurement context is proportional to |ψ(A)·ψ(B)|².
    """
    if measurements is not None:
        delta_phase = _pairwise_phase_diff(
            psi_a.entity, psi_b.entity, measurements
        )
    else:
        phase_a = psi_a.phase if psi_a.phase is not None else 0.0
        phase_b = psi_b.phase if psi_b.phase is not None else 0.0
        delta_phase = phase_a - phase_b

    # Interference amplitude (complex multiplication in polar form)
    amplitude = psi_a.magnitude * psi_b.magnitude * math.cos(delta_phase)

    # Intensity = |amplitude|² (what you actually observe)
    cos_term = math.cos(delta_phase / 2) ** 2
    intensity = psi_a.magnitude * psi_b.magnitude * cos_term

    # Classify
    if cos_term > 0.75:
        resonance = "constructive"
    elif cos_term < 0.25:
        resonance = "destructive"
    else:
        resonance = "partial"

    logger.info(
        f"Interference {psi_a.entity}×{psi_b.entity}: "
        f"intensity={intensity:.4f}, Δφ={delta_phase:.3f}, {resonance}"
    )

    return {
        "entities": (psi_a.entity, psi_b.entity),
        "amplitude": amplitude,
        "intensity": intensity,
        "phase_diff": delta_phase,
        "cos_term": cos_term,
        "resonance": resonance,
    }


def _pairwise_phase_diff(
    entity_a: str, entity_b: str, measurements: list[dict],
    decay_hours: float = 1.0,
) -> float:
    """
    Compute phase difference from temporal co-occurrence of measurements.

    For each measurement of A, find the nearest measurement of B (in time).
    The average temporal gap, mapped through a decay function, gives the
    phase difference.

    Close in time → small Δφ → constructive interference
    Far apart → large Δφ → destructive interference

    The decay_hours parameter sets the timescale: measurements within
    decay_hours of each other are "in phase." Beyond that, phase diverges
    toward π (maximum destructive interference).

    This is the true name: the relationship between A and B is defined
    by when they were observed relative to each other, and that relationship
    is different for every pair.
    """
    times_a = []
    times_b = []

    for m in measurements:
        try:
            t = _parse_time(m["timestamp"])
        except (KeyError, ValueError):
            continue

        if m.get("subject") == entity_a or m.get("object") == entity_a:
            times_a.append(t)
        if m.get("subject") == entity_b or m.get("object") == entity_b:
            times_b.append(t)

    if not times_a or not times_b:
        return math.pi  # No data → maximally out of phase

    # For each measurement of A, find the minimum time gap to any measurement of B
    min_gaps = []
    for ta in times_a:
        gaps = [abs((ta - tb).total_seconds()) / 3600.0 for tb in times_b]
        min_gaps.append(min(gaps))

    # Average minimum gap (hours)
    avg_gap = sum(min_gaps) / len(min_gaps)

    # Map gap to phase difference [0, π] via exponential decay
    # gap=0 → Δφ=0 (perfect alignment)
    # gap=∞ → Δφ=π (complete opposition)
    # gap=decay_hours → Δφ≈π/2 (half-way)
    delta_phase = math.pi * (1 - math.exp(-avg_gap / decay_hours))

    return delta_phase


# =============================================================================
# Full wave function construction
# =============================================================================


def compute_wave(
    subject: str,
    measurements: list[dict],
    reference_time: Optional[str] = None,
) -> WaveAmplitude:
    """
    Construct the full wave function ψ for a concept.

    ψ = magnitude · e^(i·phase)

    magnitude = confidence-weighted measurement density
                (how strongly this concept has been established)
    phase     = temporal centroid relative to reference frame
                (where this concept sits in its oscillation cycle)
    coefficients = per-predicate breakdown
                   (the spectral decomposition — which frequencies contribute)

    This replaces the stub in core.py's observe_context.
    """
    subject_measurements = [m for m in measurements if m["subject"] == subject]

    if not subject_measurements:
        return WaveAmplitude(
            entity=subject,
            coefficients=[],
            magnitude=0.0,
            phase=0.0,
        )

    # Magnitude: confidence-weighted, normalized by measurement count
    # More measurements with high confidence = higher magnitude
    confidences = [m.get("confidence", 0.5) for m in subject_measurements]
    magnitude = sum(confidences) / len(confidences)

    # Per-predicate coefficients (spectral decomposition)
    # Each predicate type is a "frequency" — how this concept vibrates
    predicate_strengths = {}
    for m in subject_measurements:
        pred = m.get("predicate", "unknown")
        conf = m.get("confidence", 0.5)
        if pred not in predicate_strengths:
            predicate_strengths[pred] = []
        predicate_strengths[pred].append(conf)

    # Coefficient for each predicate = average confidence of that relationship type
    coefficients = [
        sum(confs) / len(confs)
        for confs in predicate_strengths.values()
    ]

    # Phase: temporal structure
    phase = compute_phase(subject_measurements, reference_time)

    return WaveAmplitude(
        entity=subject,
        coefficients=coefficients,
        magnitude=magnitude,
        phase=phase,
        # wu wei: attach extra context
        predicates=list(predicate_strengths.keys()),
        frequency=compute_frequency(subject_measurements),
        measurement_count=len(subject_measurements),
    )


# =============================================================================
# Helpers
# =============================================================================


def _parse_time(ts: str) -> datetime:
    """Parse ISO timestamp, tolerant of common formats."""
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return datetime.fromisoformat(ts)
