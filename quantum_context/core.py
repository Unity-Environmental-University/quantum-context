"""
Minimal quantum context implementation.

Storage: NDJSON
Math: Wave interference (no explicit primes)
Philosophy: Shor-equivalent divisibility preservation
"""

import json
import logging
import math
from pathlib import Path
from datetime import datetime
from statistics import median

from quantum_context.models import Measurement, WaveAmplitude, DependencyGraph

logger = logging.getLogger(__name__)

# Storage location
GRAPH_FILE = Path.home() / ".quantum-context" / "graph.ndjson"


# =============================================================================
# OBSERVE - Low friction
# =============================================================================


def observe_context(subject: str, *, observer: str = "claude") -> WaveAmplitude:
    """
    Read measurements about a subject. No side effects.

    Projects wave function ψ onto this entity from observer's frame.
    Magnitude is recency-weighted confidence. Phase is age of most recent
    measurement normalized to the data's own timescale.
    """
    logger.info(f"Observing context: {subject} (frame: {observer})")

    measurements = _load_measurements(subject)

    if not measurements:
        logger.info(f"No measurements found for {subject}")
        return WaveAmplitude(
            entity=subject,
            coefficients=[],
            magnitude=0.0,
        )

    now = datetime.now()
    timescale = _derive_timescale(measurements)
    confidences = [m["confidence"] for m in measurements]

    if timescale > 0:
        ages = [_seconds_since(m["timestamp"], now) for m in measurements]
        weights = [math.exp(-age / timescale) for age in ages]
        total_weight = sum(weights)
        if total_weight > 0:
            magnitude = sum(c * w for c, w in zip(confidences, weights)) / total_weight
        else:
            magnitude = sum(confidences) / len(confidences)
        # Phase: age of newest measurement, normalized to timescale
        # 0.0 = just measured, 1.0 = one natural cycle ago, etc.
        newest_age = min(ages)
        phase = newest_age / timescale
    else:
        # All measurements at same instant (or single measurement)
        magnitude = sum(confidences) / len(confidences)
        phase = 0.0

    return WaveAmplitude(
        entity=subject,
        coefficients=confidences,
        magnitude=magnitude,
        phase=phase,
    )


# =============================================================================
# ANALYZE - Medium friction
# =============================================================================


def compute_mismatch(
    subject: str,
    expected_magnitude: float,
    *,
    observer: str = "claude",
) -> dict:
    """
    Measure interference between expected state and current measurements.

    All parameters derived from data. No magic numbers.
    Returns interference strength and stage classification.
    """
    current = observe_context(subject, observer=observer)

    magnitude_delta = abs(expected_magnitude - current.magnitude)
    phase = current.phase if current.phase is not None else 0.0

    # Timescale from this subject's data (already used by observe_context)
    measurements = _load_measurements(subject)
    timescale = _derive_timescale(measurements)

    # Interference: large magnitude gap + recent = strong
    # Decays with phase (time passing reduces interference)
    if timescale > 0 and phase > 0:
        interference = magnitude_delta * math.exp(-phase)
    else:
        interference = magnitude_delta

    # Stage thresholds from the whole graph's mismatch distribution
    thresholds = _derive_stage_thresholds()
    stage = _classify_stage(magnitude_delta, phase, thresholds)

    return {
        "subject": subject,
        "expected_magnitude": expected_magnitude,
        "measured_magnitude": current.magnitude,
        "magnitude_delta": magnitude_delta,
        "phase": phase,
        "timescale_seconds": timescale,
        "interference": interference,
        "stage": stage,
        "thresholds": thresholds,
    }


def analyze_dependencies(subject: str, *, independence_threshold: float = 0.3) -> DependencyGraph:
    """
    Identify divisibility structure via correlation.

    What does this concept depend on? (high correlation = shared prime factors)
    What is it independent of? (low correlation = coprime = GCD=1)

    Uses correlation as proxy for divisibility without computing primes:
    - High correlation → shared structure (GCD > 1)
    - Low correlation → independent (coprime, GCD = 1)
    """
    logger.info(f"Analyzing dependencies: {subject}")

    measurements = _load_all_measurements()

    # Find direct dependencies (objects this subject relates to)
    depends_on = []
    shared = {}

    for m in measurements:
        if m["subject"] == subject:
            # Objects this subject relates to
            obj = m["object"]
            if obj not in depends_on:
                depends_on.append(obj)
                shared[obj] = m["confidence"]

    # Find all other subjects in the graph
    all_subjects = set()
    for m in measurements:
        all_subjects.add(m["subject"])
    all_subjects.discard(subject)

    # Compute correlations to find independent concepts
    # (concepts with low correlation = coprime = orthogonal)
    independent_of = []

    for other_subject in all_subjects:
        # Skip if it's a direct dependency
        if other_subject in depends_on:
            continue

        correlation = _compute_correlation(measurements, subject, other_subject)

        if correlation < independence_threshold:
            independent_of.append(other_subject)
            logger.debug(f"{subject} ⊥ {other_subject} (correlation={correlation:.3f})")

    logger.info(f"Found {len(depends_on)} dependencies, {len(independent_of)} independent concepts")

    return DependencyGraph(
        subject=subject,
        depends_on=depends_on,
        independent_of=independent_of,
        shared_structure=shared,
    )


# =============================================================================
# ACT - High friction
# =============================================================================


def act_record(
    subject: str,
    predicate: str,
    obj: str,
    confidence: float = 0.5,
    *,
    observer: str = "claude",
    evidence: list[str] | None = None,
    confirm: bool = False,
) -> dict:
    """
    Add measurement to graph. Requires confirmation.

    Confidence ceiling: 0.7 (epistemic humility)
    To exceed 0.7: provide evidence citations

    This modifies shared reality. Deliberate action required.
    """
    if not confirm:
        raise ValueError(
            "Recording measurements requires explicit confirmation. "
            "Set confirm=True to proceed."
        )

    # Enforce confidence ceiling
    if confidence > 0.7 and not evidence:
        logger.warning(f"Confidence {confidence} capped at 0.7 (no evidence provided)")
        confidence = 0.7
    elif confidence > 0.7 and evidence:
        # Evidence allows exceeding ceiling
        logger.info(f"Confidence {confidence} accepted (evidence: {len(evidence)} citations)")

    logger.warning(f"RECORDING: {subject} {predicate} {obj} (conf={confidence})")

    measurement = {
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "confidence": min(confidence, 1.0),  # Absolute max still 1.0
        "observer": observer,
        "timestamp": datetime.now().isoformat(),
        "evidence": evidence or [],
    }

    _append_measurement(measurement)

    return {
        "status": "recorded",
        "measurement": measurement,
        "message": f"Added: {subject} {predicate} {obj}",
    }


# =============================================================================
# Storage helpers
# =============================================================================


def _load_measurements(subject: str) -> list[dict]:
    """Load all measurements for a subject."""
    if not GRAPH_FILE.exists():
        return []

    measurements = []
    with open(GRAPH_FILE, "r") as f:
        for line in f:
            m = json.loads(line)
            if m.get("subject") == subject:
                measurements.append(m)

    return measurements


def _load_all_measurements() -> list[dict]:
    """Load all measurements."""
    if not GRAPH_FILE.exists():
        return []

    measurements = []
    with open(GRAPH_FILE, "r") as f:
        for line in f:
            measurements.append(json.loads(line))

    return measurements


def _append_measurement(measurement: dict):
    """Append measurement to NDJSON file."""
    GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(GRAPH_FILE, "a") as f:
        f.write(json.dumps(measurement) + "\n")


def _seconds_since(timestamp_str: str, now: datetime) -> float:
    """Seconds elapsed since a timestamp. Handles missing/bad timestamps."""
    try:
        t = datetime.fromisoformat(timestamp_str)
        return max(0.0, (now - t).total_seconds())
    except (ValueError, TypeError):
        return 0.0


def _derive_timescale(measurements: list[dict]) -> float:
    """
    Derive the natural timescale from the data itself.

    Returns median interval between consecutive measurements (in seconds).
    If only one measurement, returns 0 (no timescale yet).
    """
    if len(measurements) < 2:
        return 0.0

    try:
        timestamps = sorted(
            datetime.fromisoformat(m["timestamp"]) for m in measurements
            if "timestamp" in m
        )
    except (ValueError, TypeError):
        return 0.0

    if len(timestamps) < 2:
        return 0.0

    intervals = [
        (timestamps[i + 1] - timestamps[i]).total_seconds()
        for i in range(len(timestamps) - 1)
    ]
    # Filter out zero-intervals (batch inserts at same instant)
    nonzero = [iv for iv in intervals if iv > 0]
    if not nonzero:
        return 0.0

    return median(nonzero)


def _derive_stage_thresholds() -> dict:
    """
    Derive mismatch stage boundaries from the graph's actual data distribution.

    Looks at all subjects, computes the spread of confidence values per subject,
    and uses quartiles of that spread to set thresholds.

    Returns {"q1": float, "q2": float, "q3": float} where:
    - magnitude_delta > q3 → denial (top quartile of observed variation)
    - magnitude_delta > q2 → load-bearing
    - magnitude_delta > q1 → integrating
    - else → resynchronized
    """
    measurements = _load_all_measurements()

    if not measurements:
        # No data: fall back to uniform splits of [0, 1]
        return {"q1": 0.25, "q2": 0.5, "q3": 0.75, "derived": False}

    # Group confidences by subject
    by_subject: dict[str, list[float]] = {}
    for m in measurements:
        subj = m["subject"]
        if subj not in by_subject:
            by_subject[subj] = []
        by_subject[subj].append(m["confidence"])

    # Compute spread (max - min confidence) per subject
    spreads = []
    for confs in by_subject.values():
        if len(confs) >= 2:
            spreads.append(max(confs) - min(confs))

    if not spreads:
        # All subjects have single measurements — use confidence variance across graph
        all_confs = [m["confidence"] for m in measurements]
        if len(all_confs) >= 2:
            mean_c = sum(all_confs) / len(all_confs)
            spread = max(abs(c - mean_c) for c in all_confs)
            spreads = [spread]
        else:
            return {"q1": 0.25, "q2": 0.5, "q3": 0.75, "derived": False}

    spreads.sort()
    n = len(spreads)
    q1 = spreads[n // 4] if n >= 4 else spreads[0] / 3
    q2 = spreads[n // 2] if n >= 2 else spreads[0] / 2
    q3 = spreads[(3 * n) // 4] if n >= 4 else spreads[-1]

    # Ensure monotonicity
    q1 = max(q1, 0.01)
    q2 = max(q2, q1 + 0.01)
    q3 = max(q3, q2 + 0.01)

    return {"q1": q1, "q2": q2, "q3": q3, "derived": True}


def _classify_stage(magnitude_delta: float, phase: float, thresholds: dict) -> str:
    """
    Classify the mismatch into a resynchronization stage.

    Uses data-derived thresholds and phase (temporal distance).
    Phase modulates: recent + large delta = denial, old + large delta = integrating.
    """
    q1 = thresholds["q1"]
    q2 = thresholds["q2"]
    q3 = thresholds["q3"]

    if magnitude_delta <= q1:
        return "resynchronized"

    # Phase < 1.0 means within one natural timescale (recent)
    if phase < 1.0:
        if magnitude_delta > q3:
            return "denial"
        elif magnitude_delta > q2:
            return "load-bearing"
        else:
            return "integrating"
    else:
        # Older: same magnitude delta, but further along in processing
        if magnitude_delta > q3:
            return "load-bearing"
        elif magnitude_delta > q2:
            return "integrating"
        else:
            return "resynchronized"


def _compute_correlation(measurements: list[dict], subj_a: str, subj_b: str) -> float:
    """
    Compute correlation between two subjects as proxy for GCD(Gödel(A), Gödel(B)).

    High correlation → shared prime factors → divisibility relationship
    Low correlation → coprime (GCD=1) → independent

    Strategy:
    - Direct dependency (A's object = B or vice versa) → strong correlation (0.8)
    - Shared "requires"/"depends-on" objects → strong correlation (shared structure)
    - Shared "uses" objects → weak correlation (shared infrastructure, not dependency)
    - Shared observers → weak correlation boost (same reference frame)
    - No overlap → zero correlation (coprime)
    """
    # Track what each subject relates to, grouped by relationship strength
    a_strong = set()  # requires, depends-on
    b_strong = set()
    a_weak = set()    # uses, has, etc
    b_weak = set()
    a_observers = set()
    b_observers = set()

    # Check for direct divisibility (one appears as object of the other)
    a_depends_on_b = False
    b_depends_on_a = False

    # Strong predicates indicate structural dependency
    strong_predicates = {"requires", "depends-on", "needs", "composed-of"}

    for m in measurements:
        if m["subject"] == subj_a:
            if m["predicate"] in strong_predicates:
                a_strong.add(m["object"])
            else:
                a_weak.add(m["object"])
            a_observers.add(m["observer"])
            if m["object"] == subj_b:
                a_depends_on_b = True

        if m["subject"] == subj_b:
            if m["predicate"] in strong_predicates:
                b_strong.add(m["object"])
            else:
                b_weak.add(m["object"])
            b_observers.add(m["observer"])
            if m["object"] == subj_a:
                b_depends_on_a = True

    # Direct dependency = strong correlation (one divides the other)
    if a_depends_on_b or b_depends_on_a:
        return 0.8

    # Shared STRONG dependencies = high correlation (shared prime factors)
    shared_strong = a_strong & b_strong
    all_strong = a_strong | b_strong

    # Shared WEAK infrastructure = low correlation (not structural dependency)
    shared_weak = a_weak & b_weak
    all_weak = a_weak | b_weak

    # Shared observers = same reference frame
    shared_observers = a_observers & b_observers
    all_observers = a_observers | b_observers

    # If no objects at all, zero correlation
    if not (all_strong or all_weak):
        return 0.0

    # Correlation primarily from shared strong dependencies
    strong_overlap = len(shared_strong) / len(all_strong) if all_strong else 0

    # Weak overlap contributes less (infrastructure sharing ≠ dependency)
    weak_overlap = len(shared_weak) / len(all_weak) if all_weak else 0

    # Observer overlap (tertiary signal)
    observer_overlap = len(shared_observers) / len(all_observers) if all_observers else 0

    # Weighted combination:
    # - Strong dependencies dominate (0.7)
    # - Weak infrastructure contributes little (0.15)
    # - Observer frame BOOSTS existing correlation (multiplier, not additive)
    base_correlation = (0.7 * strong_overlap) + (0.15 * weak_overlap)

    # Observer overlap boosts correlation only if there's already structural overlap
    # (same observer seeing independent things doesn't make them dependent)
    if base_correlation > 0:
        observer_boost = 1.0 + (0.5 * observer_overlap)  # Up to 1.5x boost
        correlation = min(base_correlation * observer_boost, 1.0)
    else:
        correlation = 0.0

    return correlation


# Done: Phase computation from timestamps (v0.3.0)
# Done: Mismatch detection with data-derived thresholds (v0.3.0)
# Done: Recency-weighted magnitude (v0.3.0)
# Future: Wave function fitting (periodic basis decomposition beyond weighted mean)
# Future: Frame transformations (change observer reference point)
