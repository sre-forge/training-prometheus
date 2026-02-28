from __future__ import annotations

from dataclasses import dataclass

from .models import DEFAULT_SRE_CONTRACT_V1, EnvironmentProfileSnapshot, SemanticMapping


DEFAULT_MAPPING_RULES = {
    "cpu_usage": ("container_cpu_usage_seconds_total", "sum(rate({metric}[5m])) by (namespace, workload)"),
    "memory_usage": ("container_memory_working_set_bytes", "sum({metric}) by (namespace, workload)"),
    "cpu_limit": ("kube_pod_container_resource_limits_cpu_cores", "sum({metric}) by (namespace, workload)"),
    "network_rx": ("container_network_receive_bytes_total", "sum(rate({metric}[5m])) by (namespace, workload)"),
    "connection_count": ("node_netstat_Tcp_CurrEstab", "sum({metric}) by (instance)"),
    "file_descriptors": ("process_open_fds", "sum({metric}) by (job, instance)"),
    "thread_count": ("process_threads", "sum({metric}) by (job, instance)"),
    "saturation": ("node_load1", "avg({metric}) by (instance)"),
    "error_rate": ("http_requests_total", "sum(rate({metric}{{code=~\"5..\"}}[5m])) / sum(rate({metric}[5m]))"),
}


@dataclass
class PromSemanticMapper:
    contract_domains: list[str] | None = None

    def map(self, snapshot: EnvironmentProfileSnapshot) -> SemanticMapping:
        available = {m["name"] for m in snapshot.metrics}
        domains = self.contract_domains or DEFAULT_SRE_CONTRACT_V1

        mappings: dict[str, str] = {}
        unmapped: list[str] = []

        for domain in domains:
            rule = DEFAULT_MAPPING_RULES.get(domain)
            if not rule:
                unmapped.append(domain)
                continue
            metric, template = rule
            if metric in available:
                mappings[domain] = template.format(metric=metric)
            else:
                unmapped.append(domain)

        return SemanticMapping(
            contract_version="v1",
            domain_to_query_template=dict(sorted(mappings.items())),
            unmapped_domains=sorted(unmapped),
        )
