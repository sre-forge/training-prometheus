from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
import json


DEFAULT_SRE_CONTRACT_V1 = [
    "cpu_usage",
    "memory_usage",
    "cpu_limit",
    "network_rx",
    "connection_count",
    "file_descriptors",
    "thread_count",
    "saturation",
    "error_rate",
]


@dataclass(frozen=True)
class EnvironmentDescriptor:
    environment_name: str
    prometheus_endpoint: str
    namespace_scope: list[str]
    cluster_type: str = "kubernetes"
    retention_days: int = 7
    scrape_interval: str = "30s"
    sre_contract_version: str = "v1"

    @classmethod
    def from_file(cls, path: str) -> "EnvironmentDescriptor":
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def deterministic_fingerprint(self) -> str:
        raw = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class EnvironmentProfileSnapshot:
    generated_at: str
    metrics: list[dict[str, Any]]
    label_keys: list[str]
    exporters: list[str]
    scrape_characteristics: dict[str, Any]
    descriptor_fingerprint: str

    @classmethod
    def build(
        cls,
        metrics: list[dict[str, Any]],
        descriptor: EnvironmentDescriptor,
    ) -> "EnvironmentProfileSnapshot":
        label_keys = sorted({k for m in metrics for k in m.get("labels", {}).keys()})
        exporters = sorted({m.get("exporter", "unknown") for m in metrics})
        return cls(
            generated_at=datetime.now(timezone.utc).isoformat(),
            metrics=sorted(metrics, key=lambda m: m["name"]),
            label_keys=label_keys,
            exporters=exporters,
            scrape_characteristics={
                "scrape_interval": descriptor.scrape_interval,
                "retention_days": descriptor.retention_days,
            },
            descriptor_fingerprint=descriptor.deterministic_fingerprint(),
        )


@dataclass
class TopologyModel:
    namespaces: list[str]
    nodes: list[str]
    workloads: dict[str, list[str]]


@dataclass
class SemanticMapping:
    contract_version: str
    domain_to_query_template: dict[str, str]
    unmapped_domains: list[str] = field(default_factory=list)


@dataclass
class QueryValidationResult:
    domain: str
    query: str
    instant_ok: bool
    range_ok: bool
    cardinality: int
    anomalies: list[str]


@dataclass
class StabilityReport:
    passed: bool
    query_latencies_ms: dict[str, float]
    cardinalities: dict[str, int]
    risks: list[str]


@dataclass
class GovernanceMetadata:
    schema_version: str
    generated_at: str
    descriptor_fingerprint: str
    artifact_checksum: str
    pipeline_version: str = "0.1.0"
