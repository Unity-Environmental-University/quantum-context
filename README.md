# Quantum Context

Observer-relative knowledge graph using wave function compression for AI instance continuity.

## What This Solves

**Problem:** Claude instances don't share context across sessions. Each new conversation starts from scratch.

**Solution:** Store measurements (subject, predicate, object, confidence) from different observers in a shared graph. Wave function compression preserves causal relationships while allowing multiple perspectives.

## Install

```bash
git clone https://github.com/Unity-Environmental-University/claude-skill-starter.git
cd claude-skill-starter/quantum-context
pip install -e .
```

## Quick Start

```python
from quantum_context import observe_context, analyze_dependencies, act_record

# Record what you built this session (requires confirmation)
act_record(
    "skill-starter-template",
    "status",
    "complete",
    confidence=0.7,
    observer="claude-session-2026-02-05",
    confirm=True
)

# Next session: observe what was built
amplitude = observe_context("skill-starter-template")
# → magnitude: 0.7 (reasonably confident it's done)

deps = analyze_dependencies("skill-starter-template")
# → depends_on: ["complete", "friction-gradient-philosophy"]
```

## Key Features

### Epistemic Humility
- **Confidence ceiling: 0.7** without evidence (can't claim >70% certainty from single observation)
- **Evidence required** to exceed 0.7 (provide URLs/citations)
- **Default: 0.5** (moderate uncertainty)

```python
# Capped at 0.7
act_record("concept", "is", "true", confidence=0.95, confirm=True)
# → Actually stored as 0.7

# Evidence allows exceeding ceiling
act_record("concept", "is", "proven", confidence=0.95,
           evidence=["https://paper.pdf"], confirm=True)
# → Stored as 0.95
```

### Friction Gradient
- **observe**: No friction (read-only, always safe)
- **analyze**: Medium friction (computation cost)
- **act**: High friction (requires `confirm=True`)

### Observer Attribution
Every measurement has an observer. Different observers can see the same concept differently (like your dialectical_mcp bias detection, but with wave functions).

## Philosophy

**The universe is a holographic projection from ℤ where any integer can be the origin.**

Practical implications:
- **Measurements** = observations with confidence from an observer frame
- **Wave functions** = compressed representation (Shor-equivalent)
- **Interference** = relationships via quantum amplitude |ψ(A)·ψ(B)|²
- **Divisibility** = causality (if A divides B, A "causes" B)

This connects to:
- **Shor's algorithm** - prime factorization via wave interference
- **Wolfram's Ruliad** - space of all possible computations
- **Causal set theory** - time's arrow from observer entanglement

## Storage

```
~/.quantum-context/graph.ndjson
```

Each line is a JSON measurement:
```json
{"subject": "auth", "predicate": "requires", "object": "identity",
 "confidence": 0.7, "observer": "claude", "timestamp": "2026-02-05T12:00:00",
 "evidence": []}
```

**Portable:**
- Plain text (NDJSON)
- Git-friendly (line-based diffs)
- No database required
- Works anywhere Python 3.9+ runs

## Use Cases

✅ **AI continuity** - Claude instances share context across sessions
✅ **Multi-agent coordination** - Different agents record different observations
✅ **Learning analytics** - Track how understanding evolves with confidence
✅ **Bias detection** - Compare observer frames (like dialectical_mcp)
✅ **Research** - Test if wave interference preserves causal structure

❌ **NOT for legal evidence** - No chain of custody
❌ **NOT for medical/financial** - Confidence levels too low
❌ **NOT real-time** - Wave fitting takes time

## What's Implemented vs Stubbed

**Working now:**
- ✅ NDJSON storage
- ✅ Record measurements with confirmation
- ✅ Observe context (read measurements)
- ✅ Analyze dependencies (find related concepts)
- ✅ Confidence ceiling enforcement
- ✅ Evidence-based confidence boost
- ✅ Observer attribution

**Stubbed (future):**
- ⏳ Wave function fitting (currently just averages confidence)
- ⏳ Interference calculations (|ψ(A)·ψ(B)|²)
- ⏳ Frame transformations (different observer perspectives)
- ⏳ Confidence decay over time
- ⏳ Orthogonality detection (independent concepts)

## Files

- `quantum_context/core.py` - Implementation (~200 lines)
- `quantum_context/models.py` - Pydantic types with `extra="allow"`
- `skill.md` - How Claude uses this skill
- `RESPONSIBLE_USE.md` - Ethics and safety guidelines
- `README.md` - This file

## Example: Self-Modeling

A Claude instance can model itself:

```python
act_record("claude-instance-2026-02-05", "can", "write-code",
           confidence=0.7, confirm=True)
act_record("claude-instance-2026-02-05", "uncertain-about",
           "shor-equivalence", confidence=0.7, confirm=True)
act_record("claude-instance-2026-02-05", "tends-to",
           "over-engineer", confidence=0.6, confirm=True)
```

Future instances can read this and know the previous instance's capabilities, uncertainties, and biases.

## Status

**Alpha (0.1.0)** - Minimal working implementation. Wave function math is stubbed. Use for experimentation only.

## License

MIT - See LICENSE file

## Authors

Hallie Larsson, Unity Environmental University
With Claude Sonnet 4.5

---

*Measure. Compress. Interfere. Understand.*

*The structure teaches. The friction creates meaning. The waves preserve truth.*
