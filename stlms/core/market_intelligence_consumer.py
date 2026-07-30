"""
Market Intelligence Consumer — TERPISAH dari pipeline utama.
Replay, Statistics, Knowledge, Prediction, Simulation, Recommendation
BUKAN bagian pipeline. Mereka membaca 48000 Living Research Window kapan saja.
Dapat dijalankan on-demand, paralel, atau batch.
"""

import time
from typing import Optional


class MarketIntelligenceConsumer:
    """Consumer yang membaca 48000 Living Research Window."""

    def __init__(self, memory_window):
        self._memory_window = memory_window
        self._last_run: dict[str, float] = {}
        self._run_count: dict[str, int] = {}

    def run_replay(self, start: int, end: int) -> dict:
        self._record_run("replay")
        observations = self._memory_window.get_range(start, end)
        return {
            "type": "replay",
            "start": start,
            "end": end,
            "observation_count": len(observations),
            "run_id": self._generate_run_id("replay", start, end),
        }

    def run_statistics(self, domain: Optional[str] = None) -> dict:
        self._record_run("statistics")
        observations = self._memory_window.get_all()
        return {
            "type": "statistics",
            "domain": domain,
            "sample_size": len(observations),
            "run_id": self._generate_run_id("statistics", domain),
        }

    def run_knowledge(self, entity: Optional[str] = None) -> dict:
        self._record_run("knowledge")
        observations = self._memory_window.get_all()
        return {
            "type": "knowledge",
            "entity": entity,
            "sample_size": len(observations),
            "run_id": self._generate_run_id("knowledge", entity),
        }

    def run_prediction(self) -> dict:
        self._record_run("prediction")
        live = self._memory_window.get_live()
        return {
            "type": "prediction",
            "live_available": live is not None,
            "window_size": self._memory_window.size,
            "run_id": self._generate_run_id("prediction"),
        }

    def run_simulation(self, mode: str = "PASS") -> dict:
        self._record_run("simulation")
        observations = self._memory_window.get_all()
        return {
            "type": "simulation",
            "mode": mode,
            "sample_size": len(observations),
            "run_id": self._generate_run_id("simulation", mode),
        }

    def run_recommendation(self) -> dict:
        self._record_run("recommendation")
        observations = self._memory_window.get_all()
        return {
            "type": "recommendation",
            "sample_size": len(observations),
            "run_id": self._generate_run_id("recommendation"),
        }

    def run_all(self) -> dict:
        results = {}
        results["replay"] = self.run_replay(0, 48000)
        results["statistics"] = self.run_statistics()
        results["knowledge"] = self.run_knowledge()
        results["prediction"] = self.run_prediction()
        results["simulation"] = self.run_simulation()
        results["recommendation"] = self.run_recommendation()
        return results

    def get_consumer_status(self) -> dict:
        return {
            "last_run": self._last_run,
            "run_count": self._run_count,
            "window_size": self._memory_window.size,
            "window_max": getattr(self._memory_window, "max_size", 48000),
            "is_full": getattr(self._memory_window, "is_full", False),
        }

    def _record_run(self, run_type: str):
        self._last_run[run_type] = time.time()
        self._run_count[run_type] = self._run_count.get(run_type, 0) + 1

    @staticmethod
    def _generate_run_id(*parts) -> str:
        import hashlib
        payload = "|".join(str(p) for p in parts) + str(time.time())
        return hashlib.sha256(payload.encode()).hexdigest()[:16]
