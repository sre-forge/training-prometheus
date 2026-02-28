from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .adapters import DeterministicQueryExecutor
from .io import write_json
from .models import EnvironmentDescriptor
from .profiler import PromEnvProfiler
from .query_validator import PromQueryValidator
from .semantic_mapper import PromSemanticMapper
from .skill_governance import PromSkillGovernance
from .stability_evaluator import PromStabilityEvaluator
from .static_skill_compiler import PromStaticSkillCompiler


class TrainingPipeline:
    def __init__(
        self,
        profiler: PromEnvProfiler,
        mapper: PromSemanticMapper | None = None,
        validator: PromQueryValidator | None = None,
        evaluator: PromStabilityEvaluator | None = None,
        governance: PromSkillGovernance | None = None,
        compiler: PromStaticSkillCompiler | None = None,
    ) -> None:
        self.profiler = profiler
        self.mapper = mapper or PromSemanticMapper()
        self.validator = validator or PromQueryValidator(executor=DeterministicQueryExecutor())
        self.evaluator = evaluator or PromStabilityEvaluator()
        self.governance = governance or PromSkillGovernance()
        self.compiler = compiler or PromStaticSkillCompiler()

    def run(
        self,
        descriptor: EnvironmentDescriptor,
        out_dir: str,
        latency_overrides: dict[str, float] | None = None,
    ) -> dict:
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        snapshot, topology = self.profiler.profile(descriptor)
        mapping = self.mapper.map(snapshot)
        validation_results = self.validator.validate(mapping)

        latencies = latency_overrides or {}
        for result in validation_results:
            latencies.setdefault(result.domain, 100.0)

        stability = self.evaluator.evaluate(validation_results, latencies)
        metadata = self.governance.build_metadata(descriptor, mapping, stability)

        write_json(out_path / "environment_profile_snapshot.json", snapshot)
        write_json(out_path / "topology_model.json", topology)
        write_json(out_path / "semantic_mapping.json", mapping)
        write_json(out_path / "validation_report.json", [asdict(x) for x in validation_results])
        write_json(out_path / "stability_report.json", stability)

        compiled = None
        if stability.passed:
            compiled = str(self.compiler.compile(descriptor, mapping, stability, metadata, out_dir))

        return {
            "compiled_skill_dir": compiled,
            "stability_passed": stability.passed,
            "risks": stability.risks,
            "unmapped_domains": mapping.unmapped_domains,
        }
