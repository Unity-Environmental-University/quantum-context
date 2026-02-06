"""
Minimal quantum context implementation.

Storage: NDJSON
Math: Wave interference (no explicit primes)
Philosophy: Shor-equivalent divisibility preservation
"""

import json
import logging
from pathlib import Path
from datetime import datetime

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

    # Fit simple wave function (stub - replace with actual fitting)
    # For now: just average confidence as magnitude
    avg_confidence = sum(m["confidence"] for m in measurements) / len(measurements)

    return WaveAmplitude(
        entity=subject,
        coefficients=[avg_confidence],  # Stub: should be actual ψ coefficients
        magnitude=avg_confidence,
    )


# =============================================================================
# ANALYZE - Medium friction
# =============================================================================


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


# Future: Add wave function fitting (beyond correlation)
# Future: Add interference calculations (|ψ(A)·ψ(B)|²)
# Future: Add frame transformations (change observer reference point)
