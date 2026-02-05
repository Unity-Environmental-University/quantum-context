"""
Property-based tests for the paradigm itself.

Not testing "does it work" - testing "does it enforce the philosophy."

See docs/friction-gradient.md for explanation of the pattern.
"""

import pytest
from hypothesis import given, strategies as st

from my_skill import observe_issues, analyze_patterns, act_create_issue
from my_skill.models import IssueState, IssuePattern, Issue


# =============================================================================
# PROPERTY: Friction gradient is enforced
# =============================================================================


@given(repo=st.text(min_size=1))
def test_observe_never_requires_confirmation(repo):
    """
    Property: Observation has no friction.

    No matter what input, observe should never raise ValueError about confirmation.
    """
    try:
        observe_issues(repo)
    except ValueError as e:
        if "confirmation" in str(e).lower():
            pytest.fail("observe_issues should never require confirmation")


@given(repo=st.text(min_size=1))
def test_analyze_never_requires_confirmation(repo):
    """
    Property: Analysis has no confirmation friction.

    Understanding should be frictionless (though it might fail for other reasons).
    """
    try:
        analyze_patterns(repo)
    except ValueError as e:
        if "confirmation" in str(e).lower():
            pytest.fail("analyze_patterns should never require confirmation")


@given(
    repo=st.text(min_size=1),
    title=st.text(min_size=1),
    body=st.text(),
)
def test_act_always_requires_confirmation(repo, title, body):
    """
    Property: Action ALWAYS requires explicit confirmation.

    No matter what inputs, act_create_issue with confirm=False must raise ValueError.
    This is the core of the friction gradient.
    """
    with pytest.raises(ValueError, match="confirmation"):
        act_create_issue(repo, title, body, confirm=False)


@given(
    repo=st.text(min_size=1),
    title=st.text(min_size=1),
    body=st.text(),
)
def test_dry_run_is_default(repo, title, body):
    """
    Property: Actions default to dry_run=True.

    Safety by default. Explicit opt-in to actual execution.
    """
    result = act_create_issue(repo, title, body, confirm=True)  # Note: dry_run not specified

    # Should return dict (dry run) not Issue (actual execution)
    assert isinstance(result, dict), "Default should be dry_run=True"
    assert result.get("simulated") is True, "Should be simulated by default"


# =============================================================================
# PROPERTY: Wu wei (extra="allow") is enforced
# =============================================================================


@given(
    extra_field=st.text(min_size=1, alphabet=st.characters(whitelist_categories=("L",))),
    extra_value=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
)
def test_models_accept_extra_fields(extra_field, extra_value):
    """
    Property: All models have extra="allow".

    This is wu wei - we accept what emerges from the API.
    """
    # Test each model accepts arbitrary fields
    state = IssueState(
        repo="test/repo",
        open_count=10,
        closed_count=5,
        velocity=1.5,
        **{extra_field: extra_value}
    )

    # The extra field should be preserved
    dumped = state.model_dump()
    assert extra_field in dumped, f"extra='allow' should preserve {extra_field}"
    assert dumped[extra_field] == extra_value


@given(
    open_count=st.integers(min_value=0, max_value=10000),
    closed_count=st.integers(min_value=0, max_value=10000),
    velocity=st.floats(min_value=-100, max_value=100, allow_nan=False),
)
def test_models_validate_known_fields(open_count, closed_count, velocity):
    """
    Property: Models validate what they know, accept what they don't.

    Known fields get validated (e.g., open_count must be int).
    Unknown fields get accepted (extra="allow").
    """
    state = IssueState(
        repo="test/repo",
        open_count=open_count,
        closed_count=closed_count,
        velocity=velocity,
    )

    assert state.open_count == open_count
    assert state.closed_count == closed_count
    assert state.velocity == velocity


# =============================================================================
# PROPERTY: Export order reflects priority
# =============================================================================


def test_export_order_teaches_priority():
    """
    Property: __all__ order is observe → analyze → act.

    This isn't a fuzz test, but it validates that the structure teaches.
    """
    from my_skill import __all__

    observe_index = __all__.index("observe_issues")
    analyze_index = __all__.index("analyze_patterns")
    act_index = __all__.index("act_create_issue")

    assert observe_index < analyze_index < act_index, (
        "Export order must reflect friction gradient: observe → analyze → act"
    )


# =============================================================================
# PROPERTY: Logging is transparent
# =============================================================================


def test_all_operations_log(caplog):
    """
    Property: All operations log their actions.

    Transparency is non-negotiable.
    """
    import logging
    caplog.set_level(logging.INFO)

    # Test with fixed inputs (caplog doesn't work with @given)
    observe_issues("test/repo")
    assert any("test/repo" in record.message for record in caplog.records), (
        "observe_issues must log"
    )

    caplog.clear()

    analyze_patterns("test/repo")
    assert any("test/repo" in record.message for record in caplog.records), (
        "analyze_patterns must log"
    )


# =============================================================================
# What these tests teach:
#
# 1. The friction gradient is ENFORCED not suggested
# 2. Wu wei is STRUCTURAL not aspirational
# 3. Export order is MEANINGFUL not arbitrary
# 4. Transparency is DEFAULT not optional
#
# The tests validate the paradigm, not just the implementation.
# =============================================================================
