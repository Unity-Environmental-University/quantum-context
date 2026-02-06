# Changelog

All notable changes to quantum-context will be documented in this file.

## [0.2.0] - 2026-02-06

### Fixed
- **Major fix**: `independent_of` field in `analyze_dependencies()` now works correctly
  - Previously always returned empty list (misleading!)
  - Now uses correlation-based orthogonality detection
  - Distinguishes strong dependencies (`requires`) from weak infrastructure (`uses`)
  - Observer frame boosts correlation multiplicatively, doesn't create false correlations

### Added
- **CLI interface**: Install and use via `quantum-context` command
  - `quantum-context observe <subject>` - Read context
  - `quantum-context analyze <subject>` - Analyze dependencies
  - `quantum-context record <subject> <predicate> <object>` - Add measurements
  - `quantum-context list` - View all measurements
  - `quantum-context export` - Export as JSON/NDJSON
- Correlation-based independence detection (no prime computation needed!)
- Principled independence threshold (0.3) derived from correlation structure
- Examples directory with validation tests

### Changed
- Correlation algorithm now distinguishes strong vs weak predicates
- Observer overlap is multiplicative boost, not additive
- Default independence threshold raised from 0.2 to 0.3 (more principled)

### Implementation Details
The correlation formula preserves divisibility structure without computing primes:
```python
base_correlation = (0.7 * strong_overlap) + (0.15 * weak_overlap)
if base_correlation > 0:
    observer_boost = 1.0 + (0.5 * observer_overlap)
    correlation = min(base_correlation * observer_boost, 1.0)
```

This works because:
- High correlation → shared prime factors → GCD > 1 → dependent
- Low correlation → coprime → GCD = 1 → independent
- Graph structure is isomorphic to number-theoretic structure

## [0.1.0] - 2026-02-05

### Added
- Initial release
- NDJSON storage
- Observer-relative measurements
- Confidence ceiling (0.7 without evidence)
- MCP server integration
- Friction gradient (observe/analyze/act)
- Epistemic humility built-in
