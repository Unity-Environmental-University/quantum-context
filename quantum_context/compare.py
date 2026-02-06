"""
Observer frame comparison - see how different observers view the same concepts.

This enables bias detection, multi-perspective analysis, and dialectical reasoning.
"""

import logging
from typing import Dict, List, Tuple
from quantum_context.core import _load_all_measurements
from quantum_context.models import WaveAmplitude

logger = logging.getLogger(__name__)


def compare_observers(
    subject: str,
    observer_a: str,
    observer_b: str
) -> Dict:
    """
    Compare how two observers see the same subject.

    Returns confidence differences, objects seen by only one observer,
    and shared vs divergent perspectives.

    This is low friction (observe) - read only, no side effects.
    """
    logger.info(f"Comparing observers: {observer_a} vs {observer_b} on {subject}")

    measurements = _load_all_measurements()

    # Filter measurements for this subject by each observer
    a_measurements = [m for m in measurements
                     if m["subject"] == subject and m["observer"] == observer_a]
    b_measurements = [m for m in measurements
                     if m["subject"] == subject and m["observer"] == observer_b]

    # Extract what each observer recorded
    a_objects = {m["object"]: m for m in a_measurements}
    b_objects = {m["object"]: m for m in b_measurements}

    # Find shared and unique observations
    shared_objects = set(a_objects.keys()) & set(b_objects.keys())
    only_a = set(a_objects.keys()) - set(b_objects.keys())
    only_b = set(b_objects.keys()) - set(a_objects.keys())

    # Compare confidence for shared observations
    confidence_deltas = {}
    for obj in shared_objects:
        conf_a = a_objects[obj]["confidence"]
        conf_b = b_objects[obj]["confidence"]
        confidence_deltas[obj] = {
            "observer_a_confidence": conf_a,
            "observer_b_confidence": conf_b,
            "delta": conf_b - conf_a,
            "predicate_a": a_objects[obj]["predicate"],
            "predicate_b": b_objects[obj]["predicate"],
        }

    # Compute overall agreement
    if len(a_measurements) > 0 and len(b_measurements) > 0:
        jaccard = len(shared_objects) / len(set(a_objects.keys()) | set(b_objects.keys()))
    else:
        jaccard = 0.0

    return {
        "subject": subject,
        "observer_a": observer_a,
        "observer_b": observer_b,
        "agreement": jaccard,
        "shared_observations": list(shared_objects),
        "only_observer_a": list(only_a),
        "only_observer_b": list(only_b),
        "confidence_deltas": confidence_deltas,
        "observer_a_count": len(a_measurements),
        "observer_b_count": len(b_measurements),
    }


def detect_systematic_bias(
    observer: str,
    reference_observer: str = "claude",
    min_measurements: int = 3
) -> Dict:
    """
    Detect systematic bias in an observer's measurements.

    Compares an observer against a reference to find:
    - Consistent over/under confidence
    - Topics only this observer sees
    - Blind spots (topics they miss)

    This is analyze (medium friction) - computes patterns but read-only.
    """
    logger.info(f"Detecting systematic bias: {observer} vs {reference_observer}")

    measurements = _load_all_measurements()

    # Get all subjects measured by both
    observer_subjects = {m["subject"] for m in measurements if m["observer"] == observer}
    reference_subjects = {m["subject"] for m in measurements if m["observer"] == reference_observer}

    # Subjects both measured
    shared_subjects = observer_subjects & reference_subjects

    if len(shared_subjects) < min_measurements:
        return {
            "error": f"Not enough shared measurements (need {min_measurements}, have {len(shared_subjects)})",
            "observer": observer,
            "reference": reference_observer,
        }

    # Analyze confidence patterns
    confidence_bias = []
    for subj in shared_subjects:
        comparison = compare_observers(subj, observer, reference_observer)
        for obj, delta_info in comparison["confidence_deltas"].items():
            confidence_bias.append(delta_info["delta"])

    avg_bias = sum(confidence_bias) / len(confidence_bias) if confidence_bias else 0.0

    # Determine bias type
    if avg_bias > 0.1:
        bias_type = "overconfident"
    elif avg_bias < -0.1:
        bias_type = "underconfident"
    else:
        bias_type = "calibrated"

    return {
        "observer": observer,
        "reference": reference_observer,
        "bias_type": bias_type,
        "average_confidence_delta": avg_bias,
        "shared_subjects": list(shared_subjects),
        "only_observer": list(observer_subjects - reference_subjects),
        "blind_spots": list(reference_subjects - observer_subjects),
        "sample_size": len(confidence_bias),
    }
