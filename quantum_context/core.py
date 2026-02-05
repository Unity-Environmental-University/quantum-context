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


def analyze_dependencies(subject: str) -> DependencyGraph:
    """
    Identify divisibility structure.

    What does this concept depend on? (high projection)
    What is it independent of? (orthogonal)
    """
    logger.info(f"Analyzing dependencies: {subject}")

    measurements = _load_all_measurements()

    # Find related concepts via measurements
    depends_on = []
    independent_of = []
    shared = {}

    for m in measurements:
        if m["subject"] == subject:
            # Objects this subject relates to
            obj = m["object"]
            if obj not in depends_on:
                depends_on.append(obj)
                shared[obj] = m["confidence"]

    return DependencyGraph(
        subject=subject,
        depends_on=depends_on,
        independent_of=independent_of,  # Stub: should compute orthogonality
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


# Future: Add wave function fitting
# Future: Add interference calculations
# Future: Add frame transformations
