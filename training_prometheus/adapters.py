from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import random


@dataclass
class FilePrometheusReader:
    """Read metric metadata from a JSON file for deterministic training."""

    metrics_file: str

    def list_metric_metadata(self) -> list[dict]:
        with open(self.metrics_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict) and "metrics" in payload:
            return payload["metrics"]
        if isinstance(payload, list):
            return payload
        raise ValueError("metrics_file must contain a list or {'metrics': [...]} payload")


@dataclass
class NullKubernetesReader:
    def list_namespaces(self) -> list[str]:
        return []

    def list_nodes(self) -> list[str]:
        return []

    def list_workloads(self, namespaces: list[str]) -> dict[str, list[str]]:
        return {ns: [] for ns in namespaces}


@dataclass
class DeterministicQueryExecutor:
    seed: int = 7

    def execute_instant(self, query: str) -> list[dict]:
        rng = random.Random(f"{self.seed}:{query}:instant")
        size = rng.randint(1, 15)
        return [{"value": round(rng.random(), 6), "labels": {"series": str(i)}} for i in range(size)]

    def execute_range(self, query: str, window: str = "1h") -> list[dict]:
        rng = random.Random(f"{self.seed}:{query}:{window}:range")
        size = rng.randint(1, 20)
        return [{"value": round(rng.random(), 6), "labels": {"series": str(i)}} for i in range(size)]


def load_latencies_from_file(path: str | None) -> dict[str, float]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return {k: float(v) for k, v in payload.items()}
