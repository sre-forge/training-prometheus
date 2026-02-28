from __future__ import annotations

from dataclasses import dataclass, field

from .models import QueryValidationResult, StabilityReport


@dataclass
class StabilityPolicy:
    max_latency_ms: float = 2000.0
    max_cardinality: int = 10000


@dataclass
class PromStabilityEvaluator:
    policy: StabilityPolicy = field(default_factory=StabilityPolicy)

    def evaluate(
        self,
        validation_results: list[QueryValidationResult],
        latencies_ms: dict[str, float],
    ) -> StabilityReport:
        risks: list[str] = []
        cardinalities: dict[str, int] = {}

        for result in validation_results:
            domain = result.domain
            cardinalities[domain] = result.cardinality
            latency = latencies_ms.get(domain, 0.0)

            if latency > self.policy.max_latency_ms:
                risks.append(f"latency:{domain}")
            if result.cardinality > self.policy.max_cardinality:
                risks.append(f"cardinality:{domain}")
            for anomaly in result.anomalies:
                risks.append(f"anomaly:{domain}:{anomaly}")

        unique_risks = sorted(set(risks))
        return StabilityReport(
            passed=not unique_risks,
            query_latencies_ms=dict(sorted(latencies_ms.items())),
            cardinalities=dict(sorted(cardinalities.items())),
            risks=unique_risks,
        )
