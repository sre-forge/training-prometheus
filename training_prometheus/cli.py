from __future__ import annotations

import argparse
import json

from .adapters import FilePrometheusReader, NullKubernetesReader, load_latencies_from_file
from .models import EnvironmentDescriptor
from .pipeline import TrainingPipeline
from .profiler import PromEnvProfiler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="training-prometheus deterministic training pipeline")
    parser.add_argument("--descriptor", required=True, help="Path to environment descriptor JSON")
    parser.add_argument("--metrics", required=True, help="Path to metric metadata JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--latencies", help="Optional query latency map JSON file")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    descriptor = EnvironmentDescriptor.from_file(args.descriptor)

    profiler = PromEnvProfiler(
        prometheus_reader=FilePrometheusReader(args.metrics),
        kubernetes_reader=NullKubernetesReader(),
    )
    pipeline = TrainingPipeline(profiler=profiler)
    result = pipeline.run(
        descriptor=descriptor,
        out_dir=args.out,
        latency_overrides=load_latencies_from_file(args.latencies),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
