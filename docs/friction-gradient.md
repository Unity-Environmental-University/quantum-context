# Friction Gradient

## What It Is

A **friction gradient** means different operations have different levels of resistance.

```
LOW FRICTION ════════════════════════════════ HIGH FRICTION
    │                    │                         │
    ▼                    ▼                         ▼
 OBSERVE              ANALYZE                    ACT
    │                    │                         │
 No barriers         Takes work            Requires consent
 Fast/cheap          Moderate cost          Explicit confirmation
 Safe to try         Might cost $           Can't undo
```

## Why It Exists

**In any system, not all operations are equally consequential:**

- **Reading** doesn't change state → should be easy
- **Writing** changes state → should be deliberate
- **Analyzing** costs resources → should have moderate friction

**The interface should match the consequences:**

| Operation | Consequence | Friction |
|-----------|-------------|----------|
| `observe_issues("repo")` | No side effects | None - just works |
| `analyze_patterns("repo")` | Costs compute/time | Some - might need auth |
| `act_create_issue("repo", ...)` | Creates permanent record | High - needs `confirm=True` |

## Where This Pattern Comes From

### 1. **Human-Computer Interaction (Don Norman)**
- Easy to explore, hard to destroy
- Affordances guide behavior
- Example: Delete button is red, requires confirmation

### 2. **Security (Principle of Least Privilege)**
- Read access is default
- Write access requires permission
- Example: File systems (r/w/x permissions)

### 3. **Game Design**
- Easy to try different strategies
- Hard to commit to irreversible choices
- Example: "Are you sure you want to delete your save?"

### 4. **Ecological Systems**
- Observe without disturbing
- Intervene only when necessary
- Example: Wildlife observation vs intervention

### 5. **API Design (HTTP Methods)**
- GET: idempotent, safe, cacheable
- POST/PUT/DELETE: require authentication, not safe

## How It Works in Code

### Low Friction (Observe)
```python
def observe_issues(repo: str) -> IssueState:
    """
    No auth param.
    No confirmation param.
    Can't fail due to permissions.
    Just returns data.
    """
    return IssueState(...)
```

**Message:** "It's safe to look. Look as much as you want."

### Medium Friction (Analyze)
```python
def analyze_patterns(repo: str, *, api_key: str | None = None) -> Pattern:
    """
    Might need auth (costs API quota).
    Takes time/resources.
    But still read-only.
    """
    return IssuePattern(...)
```

**Message:** "This costs something, but won't break anything."

### High Friction (Act)
```python
def act_create_issue(
    repo: str,
    title: str,
    body: str,
    *,
    confirm: bool = False,  # Must explicitly set to True
    dry_run: bool = True,   # Safe by default
) -> Issue:
    """
    Requires confirmation.
    Defaults to dry-run.
    Can't accidentally execute.
    """
    if not confirm:
        raise ValueError("Set confirm=True")

    if dry_run:
        return {"simulated": True}

    # Actually creates the issue
```

**Message:** "This matters. Think before you act."

## What It Teaches

The gradient **teaches through structure, not documentation:**

1. **You can't accidentally act**
   - Must explicitly `confirm=True`
   - Default is `dry_run=True`
   - Two deliberate steps

2. **Observation is always safe**
   - No confirmation needed
   - No auth needed (for public data)
   - Encourages exploration

3. **The pattern is consistent**
   - All observe functions: low friction
   - All analyze functions: medium friction
   - All act functions: high friction

4. **Responsibility scales with consequence**
   - Reading: no responsibility needed
   - Analyzing: some cost/quota awareness
   - Acting: full responsibility required

## Why Not Just "Read vs Write"?

**Three levels instead of two:**

```
Read/Write model:
  read  = safe
  write = dangerous

Friction gradient model:
  observe = safe (read, no cost)
  analyze = moderate (read, has cost)
  act     = dangerous (write, permanent)
```

The middle tier matters because **not all reads are equal:**
- `observe_issues("repo")` - Free, instant
- `analyze_patterns("repo")` - Costs API quota, takes time

## Real-World Examples

### GitHub API
- GET /repos/{repo} → No auth, low friction
- GET /repos/{repo}/stats → Costs compute, medium friction
- POST /repos/{repo}/issues → Requires auth + changes state, high friction

### Medical Systems
- View patient record → Low friction (but logged)
- Run diagnostic analysis → Medium friction (costs money, takes time)
- Prescribe medication → High friction (requires confirmation, permanent)

### Game Design
- Look around → No cost
- Analyze enemy patterns → Costs attention/time
- Attack → Commits resources, can't undo

### Financial Systems
- View account balance → Low friction
- Calculate investment projections → Medium friction (computation)
- Execute trade → High friction (confirmation required, irreversible)

## How to Implement

1. **Identify operation types:**
   - What's read-only and free? → observe
   - What's read-only but costly? → analyze
   - What changes state? → act

2. **Add appropriate friction:**
   - observe: no params for auth/confirmation
   - analyze: optional auth, no confirmation
   - act: required `confirm` param, defaults to dry_run

3. **Export in order:**
   ```python
   __all__ = [
       "observe_thing",   # First
       "analyze_thing",   # Middle
       "act_on_thing",    # Last
   ]
   ```

4. **Test the gradient:**
   ```python
   test_observe_never_requires_confirmation()
   test_act_always_requires_confirmation()
   ```

## Anti-Patterns

❌ **Equal friction for all operations**
```python
def get_data(confirm=True):  # Why does reading need confirmation?
def delete_data(confirm=True):  # Same friction as reading?
```

❌ **No friction for dangerous operations**
```python
def delete_everything():  # One function call destroys everything?
    db.drop_all()
```

❌ **Too much friction for safe operations**
```python
def view_data(confirm=True, are_you_sure=True, really_sure=True):
    # Just reading shouldn't need this
```

## Summary

**Friction gradient = matching interface resistance to consequence**

- Low consequence → Low friction (observe)
- Medium consequence → Medium friction (analyze)
- High consequence → High friction (act)

The code structure teaches appropriate behavior without documentation.

Users learn: "If it asks for confirmation, it matters."

---

*Make safe things easy. Make dangerous things deliberate.*
