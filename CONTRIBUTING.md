# Contributing Guide

Thanks for contributing to `training-prometheus`.

## Scope and Principles

Before proposing changes, align with these project guarantees:

- Read-only by design: no mutation of Prometheus, cluster, or rules.
- Deterministic output: same descriptor + same inputs should produce equivalent artifacts.
- Training-first architecture: runtime discovery/guessing logic is out of scope.

See `README.md` for project-level context and phase definitions.

## Development Setup

- Python: `>=3.10`
- Run tests:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

- Run pipeline with example data:

```bash
python -m training_prometheus.cli \
  --descriptor examples/environment.qa.json \
  --metrics examples/metrics.sample.json \
  --out ./artifacts
```

## Change Types

### 1) Behavioral change
Examples:
- New mapping rule
- Validation or stability policy threshold change
- New generated artifact fields

Requirements:
- Add or update tests in `tests/`
- Update docs (`README.md` and/or this file) describing user-visible behavior
- Prefer additive changes; keep backward compatibility unless explicitly stated

### 2) Internal refactor
Examples:
- Module reorganization
- Improved dependency injection

Requirements:
- No functional regression
- Existing tests must pass
- Add targeted tests if behavior boundaries change

### 3) New feature
Examples:
- New pipeline stage
- New adapter type

Requirements:
- Keep deterministic contract explicit
- Document API/CLI/artifact impacts
- Add tests for success and failure paths

## Testing Policy

At minimum for non-trivial changes:

1. Unit tests for changed behavior.
2. Pipeline-level test proving artifact generation is still valid.
3. One CLI execution smoke test (with local examples) when CLI/runtime flow changes.

## Backward Compatibility Policy

When making breaking changes, include all of:

- A clear “Breaking Changes” note in PR description
- Migration steps for users
- Updated examples and docs

## Coding Guidance

- Favor small, composable components as in existing pipeline stages.
- Use explicit dataclass models for stage I/O where practical.
- Keep output ordering deterministic (sorted keys/lists where meaningful).
- Avoid hidden network side effects in default adapters.

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] Added/updated tests for changed behavior
- [ ] Docs updated (`README.md`, `CONTRIBUTING.md`, examples if needed)
- [ ] Determinism and read-only guarantees preserved
- [ ] CLI and generated artifact impacts clearly described
