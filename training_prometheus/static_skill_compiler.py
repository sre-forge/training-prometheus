from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from .io import write_json
from .models import EnvironmentDescriptor, GovernanceMetadata, SemanticMapping, StabilityReport


class PromStaticSkillCompiler:
    def compile(
        self,
        descriptor: EnvironmentDescriptor,
        mapping: SemanticMapping,
        stability: StabilityReport,
        metadata: GovernanceMetadata,
        out_dir: str,
    ) -> Path:
        if not stability.passed:
            raise ValueError("Stability evaluation did not pass; refusing to compile static skill")

        skill_dir = Path(out_dir) / f"sre-{descriptor.environment_name}-prometheus-query"
        skill_dir.mkdir(parents=True, exist_ok=True)

        write_json(skill_dir / "query_templates.json", mapping.domain_to_query_template)
        write_json(skill_dir / "metadata.json", asdict(metadata))
        write_json(skill_dir / "stability_report.json", asdict(stability))
        self._write_skill_md(skill_dir / "skill.md", descriptor, mapping)
        self._write_query_engine(skill_dir / "query_engine.py", mapping)
        return skill_dir

    @staticmethod
    def _write_skill_md(path: Path, descriptor: EnvironmentDescriptor, mapping: SemanticMapping) -> None:
        lines = [
            f"# sre-{descriptor.environment_name}-prometheus-query",
            "",
            "Statically compiled query skill. No runtime discovery is performed.",
            "",
            "## Domains",
        ]
        for domain, query in mapping.domain_to_query_template.items():
            lines.append(f"- `{domain}`: `{query}`")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def _write_query_engine(path: Path, mapping: SemanticMapping) -> None:
        templates_literal = json.dumps(mapping.domain_to_query_template, indent=2, sort_keys=True)
        content = f'''"""Generated static query engine."""

QUERY_TEMPLATES = {templates_literal}


def list_domains():
    return sorted(QUERY_TEMPLATES.keys())


def render_query(domain: str) -> str:
    if domain not in QUERY_TEMPLATES:
        raise KeyError(f"Unknown domain: {{domain}}")
    return QUERY_TEMPLATES[domain]
'''
        path.write_text(content, encoding="utf-8")
