"""
Tests for phase computation and mismatch detection.

Tests the actual properties, not decorative assertions.
Data-derived parameters mean we test behaviors, not specific numbers.
"""

import json
import math
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from quantum_context.core import (
    observe_context,
    compute_mismatch,
    _derive_timescale,
    _derive_stage_thresholds,
    _classify_stage,
    _seconds_since,
    GRAPH_FILE,
)


# =============================================================================
# Helpers
# =============================================================================


def _make_graph(measurements: list[dict], tmp_path: Path) -> Path:
    """Write measurements to a temp NDJSON file and patch GRAPH_FILE to it."""
    graph = tmp_path / "graph.ndjson"
    with open(graph, "w") as f:
        for m in measurements:
            f.write(json.dumps(m) + "\n")
    return graph


def _measurement(subject, predicate, obj, confidence, observer="claude",
                 timestamp=None, evidence=None):
    return {
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "confidence": confidence,
        "observer": observer,
        "timestamp": (timestamp or datetime.now()).isoformat(),
        "evidence": evidence or [],
    }


# =============================================================================
# _seconds_since
# =============================================================================


def test_seconds_since_returns_positive():
    t = (datetime.now() - timedelta(hours=1)).isoformat()
    result = _seconds_since(t, datetime.now())
    assert 3500 < result < 3700  # roughly an hour


def test_seconds_since_handles_bad_input():
    assert _seconds_since("not-a-date", datetime.now()) == 0.0
    assert _seconds_since(None, datetime.now()) == 0.0


# =============================================================================
# _derive_timescale
# =============================================================================


def test_timescale_single_measurement():
    """One measurement = no timescale (nothing to compare to)."""
    ms = [_measurement("a", "is", "b", 0.5)]
    assert _derive_timescale(ms) == 0.0


def test_timescale_two_measurements():
    """Two measurements = interval between them."""
    now = datetime.now()
    ms = [
        _measurement("a", "is", "b", 0.5, timestamp=now - timedelta(hours=2)),
        _measurement("a", "is", "c", 0.6, timestamp=now),
    ]
    ts = _derive_timescale(ms)
    assert 7100 < ts < 7300  # ~2 hours in seconds


def test_timescale_ignores_batch_inserts():
    """Measurements at the exact same time shouldn't break it."""
    now = datetime.now()
    ms = [
        _measurement("a", "is", "b", 0.5, timestamp=now),
        _measurement("a", "is", "c", 0.6, timestamp=now),
        _measurement("a", "is", "d", 0.7, timestamp=now - timedelta(hours=1)),
    ]
    ts = _derive_timescale(ms)
    # Median of nonzero intervals; there's one nonzero interval (~1 hour)
    assert 3500 < ts < 3700


def test_timescale_uses_median_not_mean():
    """Median is robust to outliers. Mean isn't."""
    now = datetime.now()
    ms = [
        _measurement("a", "is", "b", 0.5, timestamp=now - timedelta(days=365)),
        _measurement("a", "is", "c", 0.6, timestamp=now - timedelta(minutes=3)),
        _measurement("a", "is", "d", 0.7, timestamp=now - timedelta(minutes=2)),
        _measurement("a", "is", "e", 0.7, timestamp=now - timedelta(minutes=1)),
        _measurement("a", "is", "f", 0.7, timestamp=now),
    ]
    ts = _derive_timescale(ms)
    # Median interval should be ~1 minute, not pulled toward 365 days
    assert ts < 120  # under 2 minutes


# =============================================================================
# observe_context - phase computation
# =============================================================================


def test_observe_returns_phase(tmp_path):
    """observe_context now returns a phase value."""
    now = datetime.now()
    ms = [
        _measurement("auth", "requires", "identity", 0.7,
                     timestamp=now - timedelta(hours=2)),
        _measurement("auth", "uses", "jwt", 0.5,
                     timestamp=now),
    ]
    graph = _make_graph(ms, tmp_path)

    with patch("quantum_context.core.GRAPH_FILE", graph):
        result = observe_context("auth")

    assert result.phase is not None
    assert result.phase >= 0.0


def test_observe_phase_zero_when_just_measured(tmp_path):
    """If the newest measurement is right now, phase ≈ 0."""
    now = datetime.now()
    ms = [
        _measurement("auth", "requires", "identity", 0.7,
                     timestamp=now - timedelta(hours=1)),
        _measurement("auth", "uses", "jwt", 0.5, timestamp=now),
    ]
    graph = _make_graph(ms, tmp_path)

    with patch("quantum_context.core.GRAPH_FILE", graph):
        result = observe_context("auth")

    # Phase should be very small (seconds / ~3600s timescale)
    assert result.phase < 0.01


def test_observe_phase_grows_with_staleness(tmp_path):
    """Older measurements = larger phase."""
    now = datetime.now()
    # Fresh
    ms_fresh = [
        _measurement("auth", "requires", "identity", 0.7,
                     timestamp=now - timedelta(hours=1)),
        _measurement("auth", "uses", "jwt", 0.5, timestamp=now),
    ]
    # Stale (most recent was 10 timescales ago)
    ms_stale = [
        _measurement("auth", "requires", "identity", 0.7,
                     timestamp=now - timedelta(hours=11)),
        _measurement("auth", "uses", "jwt", 0.5,
                     timestamp=now - timedelta(hours=10)),
    ]

    graph_fresh = _make_graph(ms_fresh, tmp_path)
    stale_dir = tmp_path / "stale"
    stale_dir.mkdir()
    graph_stale = _make_graph(ms_stale, stale_dir)

    with patch("quantum_context.core.GRAPH_FILE", graph_fresh):
        fresh = observe_context("auth")
    with patch("quantum_context.core.GRAPH_FILE", graph_stale):
        stale = observe_context("auth")

    assert stale.phase > fresh.phase


def test_observe_recency_weights_magnitude(tmp_path):
    """Recent measurements weigh more than old ones."""
    now = datetime.now()
    ms = [
        # Old measurement: low confidence
        _measurement("auth", "requires", "identity", 0.1,
                     timestamp=now - timedelta(days=30)),
        # Recent measurement: high confidence
        _measurement("auth", "uses", "jwt", 0.7, timestamp=now),
    ]
    graph = _make_graph(ms, tmp_path)

    with patch("quantum_context.core.GRAPH_FILE", graph):
        result = observe_context("auth")

    # Magnitude should be closer to 0.7 (recent) than 0.1 (old)
    assert result.magnitude > 0.4  # plain average would be 0.4


def test_observe_no_measurements_still_works(tmp_path):
    """Empty graph doesn't crash."""
    graph = tmp_path / "graph.ndjson"
    graph.touch()

    with patch("quantum_context.core.GRAPH_FILE", graph):
        result = observe_context("nonexistent")

    assert result.magnitude == 0.0
    assert result.phase is None  # no measurements, no phase


# =============================================================================
# _derive_stage_thresholds
# =============================================================================


def test_thresholds_with_no_data(tmp_path):
    """No data = fallback thresholds, not a crash."""
    graph = tmp_path / "graph.ndjson"
    graph.touch()

    with patch("quantum_context.core.GRAPH_FILE", graph):
        t = _derive_stage_thresholds()

    assert not t["derived"]
    assert t["q1"] < t["q2"] < t["q3"]


def test_thresholds_monotonic(tmp_path):
    """q1 < q2 < q3 always, regardless of data."""
    now = datetime.now()
    ms = [
        _measurement("a", "is", "x", 0.7, timestamp=now),
        _measurement("a", "is", "y", 0.7, timestamp=now),  # no spread
        _measurement("b", "is", "x", 0.3, timestamp=now),
        _measurement("b", "is", "y", 0.3, timestamp=now),  # no spread
    ]
    graph = _make_graph(ms, tmp_path)

    with patch("quantum_context.core.GRAPH_FILE", graph):
        t = _derive_stage_thresholds()

    assert t["q1"] < t["q2"] < t["q3"]


# =============================================================================
# _classify_stage
# =============================================================================


def test_small_delta_is_resynchronized():
    """Tiny mismatch = resynchronized, regardless of phase."""
    t = {"q1": 0.1, "q2": 0.3, "q3": 0.5}
    assert _classify_stage(0.05, 0.0, t) == "resynchronized"
    assert _classify_stage(0.05, 5.0, t) == "resynchronized"


def test_large_delta_recent_is_denial():
    """Big mismatch + recent = denial."""
    t = {"q1": 0.1, "q2": 0.3, "q3": 0.5}
    assert _classify_stage(0.8, 0.5, t) == "denial"


def test_large_delta_old_is_load_bearing():
    """Big mismatch + old = further along (load-bearing, not denial)."""
    t = {"q1": 0.1, "q2": 0.3, "q3": 0.5}
    assert _classify_stage(0.8, 2.0, t) == "load-bearing"


def test_medium_delta_recent_is_load_bearing():
    t = {"q1": 0.1, "q2": 0.3, "q3": 0.5}
    assert _classify_stage(0.4, 0.5, t) == "load-bearing"


def test_medium_delta_old_is_integrating():
    t = {"q1": 0.1, "q2": 0.3, "q3": 0.5}
    assert _classify_stage(0.4, 2.0, t) == "integrating"


def test_phase_shifts_stages_forward():
    """Same magnitude delta, more time elapsed = further along in processing."""
    t = {"q1": 0.1, "q2": 0.3, "q3": 0.5}
    recent = _classify_stage(0.6, 0.5, t)
    old = _classify_stage(0.6, 2.0, t)

    stages = ["resynchronized", "integrating", "load-bearing", "denial"]
    assert stages.index(old) <= stages.index(recent)


# =============================================================================
# compute_mismatch - integration
# =============================================================================


def test_mismatch_no_data(tmp_path):
    """Mismatch against empty graph = full delta, no phase."""
    graph = tmp_path / "graph.ndjson"
    graph.touch()

    with patch("quantum_context.core.GRAPH_FILE", graph):
        result = compute_mismatch("nonexistent", 0.8)

    assert result["magnitude_delta"] == 0.8
    assert result["measured_magnitude"] == 0.0


def test_mismatch_perfect_match(tmp_path):
    """Expected = measured → zero interference."""
    now = datetime.now()
    ms = [
        _measurement("auth", "requires", "identity", 0.7, timestamp=now),
    ]
    graph = _make_graph(ms, tmp_path)

    with patch("quantum_context.core.GRAPH_FILE", graph):
        result = compute_mismatch("auth", 0.7)

    assert result["magnitude_delta"] < 0.01
    assert result["interference"] < 0.01
    assert result["stage"] == "resynchronized"


def test_mismatch_returns_all_fields(tmp_path):
    """Smoke test: all expected keys present."""
    now = datetime.now()
    ms = [
        _measurement("auth", "requires", "identity", 0.7,
                     timestamp=now - timedelta(hours=1)),
        _measurement("auth", "uses", "jwt", 0.5, timestamp=now),
    ]
    graph = _make_graph(ms, tmp_path)

    with patch("quantum_context.core.GRAPH_FILE", graph):
        result = compute_mismatch("auth", 0.2)

    expected_keys = {
        "subject", "expected_magnitude", "measured_magnitude",
        "magnitude_delta", "phase", "timescale_seconds",
        "interference", "stage", "thresholds",
    }
    assert set(result.keys()) == expected_keys


def test_mismatch_interference_decays_with_phase(tmp_path):
    """Same delta, but older data = less interference."""
    now = datetime.now()

    # Fresh data
    ms_fresh = [
        _measurement("a", "is", "x", 0.7,
                     timestamp=now - timedelta(minutes=10)),
        _measurement("a", "is", "y", 0.7, timestamp=now),
    ]
    # Stale data
    ms_stale = [
        _measurement("a", "is", "x", 0.7,
                     timestamp=now - timedelta(days=10)),
        _measurement("a", "is", "y", 0.7,
                     timestamp=now - timedelta(days=9)),
    ]

    graph_fresh = _make_graph(ms_fresh, tmp_path)
    stale_dir = tmp_path / "stale"
    stale_dir.mkdir()
    graph_stale = _make_graph(ms_stale, stale_dir)

    with patch("quantum_context.core.GRAPH_FILE", graph_fresh):
        fresh_result = compute_mismatch("a", 0.1)
    with patch("quantum_context.core.GRAPH_FILE", graph_stale):
        stale_result = compute_mismatch("a", 0.1)

    # Same magnitude delta, but stale should have less interference
    assert stale_result["interference"] < fresh_result["interference"]
