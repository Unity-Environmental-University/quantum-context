# Publishing Guide

## Quick Reference

```bash
# Push to GitHub
git push origin main
git push origin --tags

# Publish to PyPI
python -m build
python -m twine upload dist/*

# Install for local development
pip install -e .
pip install -e ".[dev]"   # With dev dependencies
pip install -e ".[mcp]"   # With MCP server support
```

## Publishing Checklist

### 1. Pre-publish Checks

- [x] Version bumped in `pyproject.toml` and `quantum_context/__init__.py`
- [x] CHANGELOG.md updated
- [x] All tests pass (`pytest`)
- [x] Code formatted (`ruff format`)
- [x] Type checks pass (`mypy quantum_context`)
- [x] Examples work
- [x] CLI works (`quantum-context --help`)
- [x] Git committed

### 2. GitHub (Already configured!)

Repository: https://github.com/Unity-Environmental-University/quantum-context

```bash
# Push changes and tags
git push origin main

# Create release tag
git tag -a v0.2.0 -m "v0.2.0: Fix independence detection + CLI"
git push origin v0.2.0
```

### 3. PyPI (Python Package Index)

**First time setup:**
```bash
pip install build twine
```

**Build and publish:**
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Check the build
twine check dist/*

# Upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ quantum-context

# If all good, upload to real PyPI
twine upload dist/*
```

**After publishing:**
Users can install with:
```bash
pip install quantum-context              # Core library
pip install quantum-context[mcp]        # With MCP support
pip install quantum-context[dev]        # With dev tools
```

### 4. Usage Modes

**As a Library:**
```python
from quantum_context import observe_context, analyze_dependencies, act_record

# Record observations
act_record("auth", "requires", "identity", confidence=0.8, confirm=True)

# Retrieve context
context = observe_context("auth")
print(f"Confidence: {context.magnitude}")

# Analyze dependencies
deps = analyze_dependencies("auth")
print(f"Depends on: {deps.depends_on}")
print(f"Independent of: {deps.independent_of}")
```

**As a CLI Tool:**
```bash
# After pip install quantum-context
quantum-context observe auth
quantum-context analyze auth
quantum-context record auth requires identity --confidence 0.8
quantum-context list
quantum-context export --format json
```

**As an MCP Server (for Claude Desktop):**
See [MCP_SETUP.md](MCP_SETUP.md) for configuration instructions.

**As a Claude Skill:**
See [skill.md](skill.md) for Claude-specific usage.

### 5. Post-publish

- [ ] Create GitHub release with CHANGELOG excerpt
- [ ] Update README badges if desired
- [ ] Announce on relevant communities
- [ ] Update documentation site (if any)

## Version Strategy

- **0.x.y** = Alpha/experimental (current)
- **1.0.0** = Stable API, wave functions fully implemented
- **2.0.0** = Breaking changes if needed

Current status: **0.2.0** (Alpha)
- Core functionality works
- Independence detection fixed
- CLI added
- Still experimental (wave functions stubbed)

## License

MIT License - See [LICENSE](LICENSE) file
