from pathlib import Path
import json
import tempfile
import unittest

from training_prometheus.adapters import FilePrometheusReader, NullKubernetesReader
from training_prometheus.models import EnvironmentDescriptor
from training_prometheus.pipeline import TrainingPipeline
from training_prometheus.profiler import PromEnvProfiler


class PipelineTest(unittest.TestCase):
    def test_full_pipeline_compiles_skill(self):
        descriptor = EnvironmentDescriptor(
            environment_name="qa",
            prometheus_endpoint="https://qa-thanos.example.com",
            namespace_scope=["sre"],
        )
        metrics_file = Path("examples/metrics.sample.json")
        profiler = PromEnvProfiler(FilePrometheusReader(str(metrics_file)), NullKubernetesReader())

        with tempfile.TemporaryDirectory() as tmp:
            result = TrainingPipeline(profiler).run(descriptor, tmp)
            self.assertTrue(result["stability_passed"])
            self.assertEqual(result["unmapped_domains"], [])
            self.assertTrue(result["compiled_skill_dir"])

            skill_dir = Path(result["compiled_skill_dir"])
            self.assertTrue((skill_dir / "skill.md").exists())
            self.assertTrue((skill_dir / "query_templates.json").exists())

    def test_artifacts_written(self):
        descriptor = EnvironmentDescriptor(
            environment_name="qa",
            prometheus_endpoint="https://qa-thanos.example.com",
            namespace_scope=["sre"],
        )
        profiler = PromEnvProfiler(FilePrometheusReader("examples/metrics.sample.json"), NullKubernetesReader())
        with tempfile.TemporaryDirectory() as tmp:
            TrainingPipeline(profiler).run(descriptor, tmp)
            report = Path(tmp) / "validation_report.json"
            self.assertTrue(report.exists())
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(payload), 1)


if __name__ == "__main__":
    unittest.main()
