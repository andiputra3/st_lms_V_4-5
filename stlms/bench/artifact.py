"""
=====================================================
MODULE:     bench/artifact.py
PURPOSE:    Benchmark Artifact — immutable benchmark_snapshot
            cards from WASIT 5-gate results.
OWNER:      BENCHMARK LAYER
=====================================================
"""

from ..core.utils import Card, wib_iso
from ..foundation.base_artifact import BaseArtifact


class BenchmarkArtifact(BaseArtifact):

    def __init__(self):
        super().__init__("BENCHMARK")

    def produce(self, wasit_result: dict, ts: int) -> Card:
        if not self.validate_input(wasit_result, ts):
            raise ValueError("Invalid Benchmark input")

        payload = {
            "gates": wasit_result.get("gates"),
            "verdict": wasit_result.get("verdict"),
            "base_metrics": wasit_result.get("base"),
            "candidate_metrics": wasit_result.get("candidate"),
            "wib_iso": wib_iso(ts),
        }

        return self.make_card("benchmark_snapshot", payload, [], ts)

    def validate_input(self, wasit_result: dict, ts: int) -> bool:
        return (wasit_result is not None and ts is not None and ts > 0)
