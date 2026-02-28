# training-prometheus

[中文版本（README.zh-CN.md）](./README.zh-CN.md)

A deterministic Prometheus environment profiler and static skill compiler for SRE query workflows.

## Overview

`training-prometheus` is a **read-only training framework** that analyzes a target Prometheus/Thanos environment and compiles a **stable, production-grade static query skill**.

It is **not** a runtime query assistant. It is a **builder system**.

Instead of relying on runtime discovery or dynamic metric guessing, this project shifts uncertainty to a controlled training phase and produces deterministic, environment-specific output.

## Why This Project Exists

Prometheus ecosystems vary heavily across organizations and clusters:

- Exporters and metric sets differ
- Labels and topology conventions differ
- Retention windows and scrape intervals differ
- Naming conventions are inconsistent
- Cardinality and query costs vary dramatically

As a result, generic query skills often fail in production because they assume metrics, labels, and aggregation patterns that do not hold in the target environment.

`training-prometheus` addresses this by learning and validating against a real environment **before** producing a production skill.

## Core Concept

The framework models the process as a deterministic compilation pipeline:

```text
Environment E
      ↓
Training Pipeline
      ↓
Semantic Model M
      ↓
Validated Query Set Q
      ↓
Static Skill S

S = Compile(E, Contract)
```

The generated skill is static, versionable, and auditable.

## Design Principles

1. **Read-only by design**
   - Never mutates Prometheus
   - Never writes recording rules
   - Never modifies cluster state
   - Only reads and analyzes

2. **Deterministic output**
   - Same environment descriptor → same generated artifacts
   - Reproducibility is required

3. **Separation of concerns**
   - Training skill: explores, learns, validates, evaluates
   - Production skill: executes only (no discovery/learning/fallback guessing)

4. **Semantic-first mapping**
   - Maps abstract SRE domains to concrete metrics
   - Avoids naive keyword-only matching

## SRE Semantic Contract (v1)

Typical semantic domains include:

- `cpu_usage`
- `memory_usage`
- `cpu_limit`
- `network_rx`
- `connection_count`
- `file_descriptors`
- `thread_count`
- `saturation`
- `error_rate`

The training pipeline maps these domains to environment-specific metric expressions and validates them end-to-end.

## Input: Environment Descriptor

The training process accepts a structured environment descriptor:

```json
{
  "environment_name": "qa",
  "prometheus_endpoint": "https://qa-thanos.example.com",
  "namespace_scope": ["sre"],
  "cluster_type": "kubernetes",
  "retention_days": 7,
  "scrape_interval": "30s",
  "sre_contract_version": "v1"
}
```

This descriptor defines the boundary and assumptions for training.

## Training Phases

### Phase 0 — Contract Definition

Define abstract SRE semantic targets.

### Phase 1 — Environment Snapshot

Collect and profile:

- Metric names
- Metric types
- Label structures
- Exporters/targets
- Scrape characteristics

Output: environment profile snapshot.

### Phase 2 — Topology Analysis

Analyze label hierarchy and workload topology (e.g., namespace, pod, container, node, workload).

Output: environment topology model.

### Phase 3 — Semantic Mapping

Map contract domains to concrete metrics and transforms.

Example:

- `cpu_usage` → `container_cpu_usage_seconds_total` + `rate()`

Output: semantic mapping model.

### Phase 4 — Query Validation

For each semantic domain:

- Build PromQL template
- Execute instant query
- Execute range query
- Validate aggregation behavior
- Inspect cardinality
- Detect NaN/zero anomalies

Output: validation report.

### Phase 5 — Stability Evaluation

Assess:

- Query latency
- Time-series cardinality
- Cross-namespace impact
- Retention-window safety
- High-cardinality risk

Output: stability report.

### Phase 6 — Skill Compilation

Only if validation and stability thresholds pass, generate static production artifacts:

```text
sre-<env>-prometheus-query/
    skill.md
    query_templates.json
    query_engine.py
    metadata.json
```

## Non-Goals

This project does **not**:

- Replace Prometheus
- Act as a dashboard product
- Perform runtime metric guessing
- Provide auto-healing logic
- Modify alert rules

It is strictly a training and compilation framework.

## Expected Production Outcomes

Compiled skills should be:

- Predictable
- Stable
- Versioned
- Auditable
- Reproducible

## Future Direction

Potential expansion areas:

- Kubernetes environment modeling
- Multi-cloud observability profiling
- Alert policy compilation
- Failure pattern modeling
- Baseline learning
- Incident knowledge integration

Long term, this project evolves toward an environment modeling and SRE capability compiler platform.

## Project Status

**Early-stage design.**

Implementation roadmap coming soon.

## Philosophy

> We do not build tools that guess.
>
> We build systems that learn first, then execute deterministically.
>
> **Training precedes production.**


## Implementation Status

This repository now includes a working reference implementation for:

- `prom-env-profiler`
- `prom-semantic-mapper`
- `prom-query-validator`
- `prom-stability-evaluator`
- `prom-static-skill-compiler`
- `prom-skill-governance` (optional metadata/checksum layer)

Main package layout:

```text
training_prometheus/
  adapters.py
  cli.py
  models.py
  profiler.py
  semantic_mapper.py
  query_validator.py
  stability_evaluator.py
  static_skill_compiler.py
  skill_governance.py
  pipeline.py
```

## Quick Start

Run with provided example inputs:

```bash
python -m training_prometheus.cli   --descriptor examples/environment.qa.json   --metrics examples/metrics.sample.json   --out ./artifacts
```

The pipeline writes intermediate artifacts and, when stable, compiles a static skill under:

```text
artifacts/sre-qa-prometheus-query/
```

## Tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
