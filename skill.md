# quantum-context

Observer-relative knowledge graph using wave function compression.

## Core Concepts

- **Measurement**: Observer records (subject, predicate, object, confidence)
- **Wave Function**: Compressed representation preserving divisibility structure
- **Frame**: Observer's reference point (which integer is "1")
- **Interference**: Relationships via quantum amplitude |ψ(A)·ψ(B)|²

## Operations

### observe context [subject]
Read measurements about a subject. No side effects.

**Returns:** Wave function amplitude, related concepts, confidence

**When:** Always start here. Observation is cheap and frame-independent.

### analyze dependencies [subject]
Identify divisibility structure (what concepts does this depend on?)

**Returns:** Dependency graph, shared structure, independence measures

**When:** After observing. Before acting. Understanding causal structure.

### act record [subject] [predicate] [object]
Add measurement to graph (requires confirmation).

**Returns:** Updated wave function, new interference patterns

**When:** Only after observation + analysis. Explicit confirmation required.

## Example Interaction

**Human:** "What do we know about authentication?"

**Claude:**
```python
# 1. Observe (low friction)
amplitude = observe_context("authentication")
# → ψ coefficients, related concepts, confidence scores

# 2. Analyze (medium friction)
deps = analyze_dependencies("authentication")
# → Depends on: identity, encryption, sessions
# → Independent of: rendering, caching

# 3. Only act if needed (high friction)
# User must explicitly request recording
```

## Procedural Rhetoric

Using this skill teaches:
- **Observation precedes action** - Must read graph before writing
- **Causal structure matters** - Dependencies = divisibility relationships
- **Frame awareness** - Different observers see different projections
- **Interference is real** - Related concepts constructively interfere

## Technical

Storage: NDJSON measurements at `~/.quantum-context/graph.ndjson`

Wave function: `ψ(entity,t) = Σ aₙ(t)·φₙ(entity)` fitted from measurements

Math: Shor's algorithm equivalence - wave interference preserves prime divisibility

Philosophy:
- Measurements = integers in prime space (implicit)
- Wave functions = efficient compression via quantum interference
- Divisibility = causal/temporal ordering
- Frames = choice of origin in ℤ ring

## Usage Context

Appropriate for:
- AI instance continuity (context across sessions)
- Multi-agent shared knowledge
- Causal reasoning (what depends on what)
- Observer-relative truth

NOT for:
- Exact symbolic proofs (use logic, not waves)
- Real-time performance (fitting takes time)
- Absolute truth claims (all observation is relative)

---

*The universe is a holographic projection from ℤ where any integer can be the origin.*

Measure. Compress. Interfere. Understand.
