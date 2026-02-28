from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .models import QueryValidationResult, SemanticMapping


class QueryExecutor(Protocol):
    def execute_instant(self, query: str) -> list[dict]: ...
    def execute_range(self, query: str, window: str = "1h") -> list[dict]: ...


@dataclass
class ValidationPolicy:
    max_cardinality: int = 5000


@dataclass
class PromQueryValidator:
    executor: QueryExecutor
    policy: ValidationPolicy = field(default_factory=ValidationPolicy)

    def validate(self, mapping: SemanticMapping) -> list[QueryValidationResult]:
        results: list[QueryValidationResult] = []

        for domain, query in mapping.domain_to_query_template.items():
            instant = self.executor.execute_instant(query)
            ranged = self.executor.execute_range(query)
            cardinality = max(len(instant), len(ranged))

            anomalies: list[str] = []
            if cardinality == 0:
                anomalies.append("empty_result")
            if cardinality > self.policy.max_cardinality:
                anomalies.append("high_cardinality")
            if any(item.get("value") is None for item in instant):
                anomalies.append("nan_detected")

            results.append(
                QueryValidationResult(
                    domain=domain,
                    query=query,
                    instant_ok=bool(instant),
                    range_ok=bool(ranged),
                    cardinality=cardinality,
                    anomalies=sorted(set(anomalies)),
                )
            )

        return sorted(results, key=lambda r: r.domain)
