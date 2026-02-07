# Theoretical Foundations

## What quantum-context Actually Does

quantum-context uses **correlation between measurements** to detect:
- Which concepts depend on each other (high correlation)
- Which concepts are independent (low correlation)
- How confident we are about relationships (evidence-weighted)

This works empirically. The code is solid. The use cases are real.

## The Deeper Question

*Why does correlation preserve conceptual structure?*

One possibility: If measurements could be encoded as integers via Gödel numbering, the correlation we compute might approximate a geometric structure on those integers.

## The Conjecture (Unproven)

**Hypothesis**: The ring of integers ℤ with the divisibility metric d(a,b) = log(lcm(a,b)/gcd(a,b)) forms a space with hyperbolic-like properties, where:
- Concepts = integers (via Gödel encoding)
- Dependencies = divisibility relationships
- Independence = coprimality (gcd = 1)
- Observer frames = choice of origin

**Status**: Interesting idea. Not proven. Possibly wrong.

## What We Actually Know

### Proven (Empirically)
✓ Triangle inequality holds for divisibility metric (1000 tests, no violations)
✓ d(1,n) = log(n) exactly (mathematical fact)
✓ Volume grows faster than polynomial (tested to n=200)
✓ Correlation preserves independence (auth ⊥ payment detected correctly)

### Not Proven
✗ Triangle inequality for all integers (need rigorous proof)
✗ Curvature is negative (haven't computed Riemann tensor)
✗ Correlation = geodesic distance (they don't match numerically!)
✗ Growth ratio stabilizes (it decreases from 3.0 → 1.65)

### What Correlation Actually Measures

Correlation computes **structural overlap** in the measurement graph:
- Shared strong relationships (requires, depends-on) → high correlation
- Shared weak relationships (uses, has) → low contribution
- Same observer → multiplicative boost (not additive)

This is NOT the same as divisibility distance, but it preserves the ordering:
- High correlation ↔ small conceptual distance
- Low correlation ↔ large conceptual distance

Good enough for practical purposes.

## Why the Geometric Interpretation Matters

Even if the ℤ holographic projection is wrong, thinking geometrically helps:
- **Metric thinking**: Distance preserves intuition about relatedness
- **Observer frames**: Different perspectives see different structures
- **Hyperbolic intuition**: Space is sparse (most concepts independent)

The tool works because it captures real structure in how concepts relate, whether or not that structure "is" hyperbolic geometry.

## Open Questions

1. Can we prove the triangle inequality rigorously?
2. What's the exact relationship between correlation and divisibility?
3. Does the growth ratio stabilize for large n?
4. Can we compute actual scalar curvature?
5. Is there a better metric that correlation approximates exactly?

## For Mathematicians

If you want to formalize this:
- Prove or disprove: d(a,b) = log(lcm(a,b)/gcd(a,b)) is a metric
- Compute Riemann curvature tensor for this metric
- Establish connection (if any) between graph correlation and geodesic distance
- Determine if space is truly hyperbolic or just "looks hyperbolic" finitely

See `experiments/hyperbolic_exploration.py` and `experiments/devils_advocate.py` for starting points.

## Practical Takeaway

**You don't need the theory to use the tool.**

quantum-context works because:
- Measurements capture real relationships
- Correlation detects structural overlap
- Evidence requirements enforce humility
- Observer attribution preserves perspective

The geometric interpretation is a lens, not a requirement.

Use it for AI continuity, multi-agent coordination, learning analytics - it works regardless of whether reality is "actually" a holographic projection from ℤ.

## Future: Phase and Temporal Tracking

**Current implementation uses magnitude only:**
- Magnitude = confidence/correlation (multiplicative structure, divisibility)
- Phase = not yet computed (additive structure, proximity)

**Complete wave function requires both:**
```
ψ(concept) = magnitude·e^(i·phase)
           = confidence·e^(i·temporal_offset)
```

**Why phase matters:**
- **Beats**: Concepts with similar magnitude but different phase interfere (auth-v1 vs auth-v2)
- **Uncanny valley**: Small additive differences create friction (proximate but not identical)
- **Temporal proximity**: Measurements close in time but different in content create interference patterns

**When to implement:**
- Priority 3: Temporal tracking
- When users ask "why does switching between similar concepts create friction?"
- When detecting "almost but not quite" relationships matters

**The two integer structures:**
1. **Multiplicative ℤ** (what we compute now): divisibility, shared structure, hierarchical
2. **Additive ℤ** (phase, future): proximity, differences, interference beats

Timestamps are already recorded. Phase computation awaits a use case that needs it.

---

*"The map is not the territory, but sometimes the map is useful."*

*"The structure teaches. The friction creates meaning. The correlation preserves truth (or at least, ordering)."*

*"Phase is the additive offset. Magnitude is the multiplicative structure. Together they make waves."*
