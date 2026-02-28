from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import EnvironmentDescriptor, EnvironmentProfileSnapshot, TopologyModel


class PrometheusReader(Protocol):
    def list_metric_metadata(self) -> list[dict]: ...


class KubernetesReader(Protocol):
    def list_namespaces(self) -> list[str]: ...
    def list_nodes(self) -> list[str]: ...
    def list_workloads(self, namespaces: list[str]) -> dict[str, list[str]]: ...


@dataclass
class PromEnvProfiler:
    prometheus_reader: PrometheusReader
    kubernetes_reader: KubernetesReader | None = None

    def profile(self, descriptor: EnvironmentDescriptor) -> tuple[EnvironmentProfileSnapshot, TopologyModel]:
        metrics = self.prometheus_reader.list_metric_metadata()
        filtered_metrics = self._filter_by_namespace(metrics, descriptor.namespace_scope)
        snapshot = EnvironmentProfileSnapshot.build(filtered_metrics, descriptor)
        topology = self._build_topology(filtered_metrics, descriptor)
        return snapshot, topology

    @staticmethod
    def _filter_by_namespace(metrics: list[dict], namespaces: list[str]) -> list[dict]:
        allowed = set(namespaces)
        if not allowed:
            return metrics
        filtered = []
        for m in metrics:
            namespace = m.get("labels", {}).get("namespace")
            if namespace is None or namespace in allowed:
                filtered.append(m)
        return filtered

    def _build_topology(self, metrics: list[dict], descriptor: EnvironmentDescriptor) -> TopologyModel:
        namespaces = sorted({m.get("labels", {}).get("namespace") for m in metrics if m.get("labels", {}).get("namespace")})
        nodes = sorted({m.get("labels", {}).get("node") for m in metrics if m.get("labels", {}).get("node")})

        workloads: dict[str, set[str]] = {}
        for metric in metrics:
            labels = metric.get("labels", {})
            ns = labels.get("namespace")
            workload = labels.get("workload")
            if ns and workload:
                workloads.setdefault(ns, set()).add(workload)

        if self.kubernetes_reader:
            namespaces = sorted(set(namespaces) | set(self.kubernetes_reader.list_namespaces()))
            nodes = sorted(set(nodes) | set(self.kubernetes_reader.list_nodes()))
            k8s_workloads = self.kubernetes_reader.list_workloads(descriptor.namespace_scope)
            for ns, items in k8s_workloads.items():
                workloads.setdefault(ns, set()).update(items)

        normalized = {k: sorted(v) for k, v in sorted(workloads.items())}
        return TopologyModel(namespaces=namespaces, nodes=nodes, workloads=normalized)
