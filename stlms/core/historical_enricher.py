"""
Tahap 16 · Historical Observation Builder
Tugas: Memperkaya seluruh artifact dengan historical context.
Enrichment TERPUSAT di satu tempat. Bukan tersebar di setiap layer.
Output: EnrichedArtifacts
"""

import hashlib
import json
from typing import Optional


class HistoricalObservationBuilder:
    """Enrichment terpusat. Satu tempat, satu tugas."""

    def __init__(self):
        self._enrichment_count = 0
        self._enriched_artifacts: dict[str, int] = {}
        self._last_enrichment_id: Optional[str] = None

    def enrich_truth(self, truth_artifact: dict, historical_truths: list[dict]) -> dict:
        enriched = dict(truth_artifact)
        enriched["historical_context"] = self._build_truth_context(historical_truths)
        enriched["enrichment_id"] = self._generate_enrichment_id("truth", truth_artifact)
        enriched["enrichment_count"] = len(historical_truths)
        self._record_enrichment("truth")
        return enriched

    def enrich_structure(self, structure_artifact: dict, historical_structures: list[dict]) -> dict:
        enriched = dict(structure_artifact)
        enriched["historical_context"] = self._build_structure_context(historical_structures)
        enriched["enrichment_id"] = self._generate_enrichment_id("structure", structure_artifact)
        enriched["enrichment_count"] = len(historical_structures)
        self._record_enrichment("structure")
        return enriched

    def enrich_statistics(self, statistics_artifact: dict, historical_statistics: list[dict]) -> dict:
        enriched = dict(statistics_artifact)
        enriched["historical_context"] = self._build_statistics_context(historical_statistics)
        enriched["enrichment_id"] = self._generate_enrichment_id("statistics", statistics_artifact)
        enriched["enrichment_count"] = len(historical_statistics)
        self._record_enrichment("statistics")
        return enriched

    def enrich_knowledge(self, knowledge_artifact: dict, historical_knowledge: list[dict]) -> dict:
        enriched = dict(knowledge_artifact)
        enriched["historical_context"] = self._build_knowledge_context(historical_knowledge)
        enriched["enrichment_id"] = self._generate_enrichment_id("knowledge", knowledge_artifact)
        enriched["enrichment_count"] = len(historical_knowledge)
        self._record_enrichment("knowledge")
        return enriched

    def enrich_prediction(self, prediction_artifact: dict, historical_predictions: list[dict]) -> dict:
        enriched = dict(prediction_artifact)
        enriched["historical_context"] = self._build_prediction_context(historical_predictions)
        enriched["enrichment_id"] = self._generate_enrichment_id("prediction", prediction_artifact)
        enriched["enrichment_count"] = len(historical_predictions)
        self._record_enrichment("prediction")
        return enriched

    def enrich_all(self, snapshot: dict, historical_data: dict) -> dict:
        result = {}
        if "truth" in snapshot:
            result["truth"] = self.enrich_truth(
                snapshot["truth"],
                historical_data.get("truths", [])
            )
        if "structure" in snapshot:
            result["structure"] = self.enrich_structure(
                snapshot["structure"],
                historical_data.get("structures", [])
            )
        if "statistics" in snapshot:
            result["statistics"] = self.enrich_statistics(
                snapshot["statistics"],
                historical_data.get("statistics", [])
            )
        if "knowledge" in snapshot:
            result["knowledge"] = self.enrich_knowledge(
                snapshot["knowledge"],
                historical_data.get("knowledge", [])
            )
        if "prediction" in snapshot:
            result["prediction"] = self.enrich_prediction(
                snapshot["prediction"],
                historical_data.get("predictions", [])
            )
        self._last_enrichment_id = hashlib.sha256(
            json.dumps(result, sort_keys=True, default=str).encode()
        ).hexdigest()
        return result

    def get_enrichment_summary(self) -> dict:
        return {
            "total_enrichments": self._enrichment_count,
            "artifacts_enriched": self._enriched_artifacts,
            "last_enrichment_id": self._last_enrichment_id,
        }

    def _generate_enrichment_id(self, artifact_type: str, artifact: dict) -> str:
        payload = {"type": artifact_type, "artifact": artifact}
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]

    def _record_enrichment(self, artifact_type: str):
        self._enrichment_count += 1
        self._enriched_artifacts[artifact_type] = self._enriched_artifacts.get(artifact_type, 0) + 1

    def _build_truth_context(self, historical_truths: list[dict]) -> dict:
        if not historical_truths:
            return {"available": False, "sample_count": 0}
        return {
            "available": True,
            "sample_count": len(historical_truths),
            "range": {
                "first_index": historical_truths[0].get("candle_index"),
                "last_index": historical_truths[-1].get("candle_index"),
            },
        }

    def _build_structure_context(self, historical_structures: list[dict]) -> dict:
        if not historical_structures:
            return {"available": False, "sample_count": 0}
        return {
            "available": True,
            "sample_count": len(historical_structures),
            "range": {
                "first_index": historical_structures[0].get("candle_index"),
                "last_index": historical_structures[-1].get("candle_index"),
            },
        }

    def _build_statistics_context(self, historical_statistics: list[dict]) -> dict:
        if not historical_statistics:
            return {"available": False, "sample_count": 0}
        return {
            "available": True,
            "sample_count": len(historical_statistics),
            "range": {
                "first_index": historical_statistics[0].get("candle_index"),
                "last_index": historical_statistics[-1].get("candle_index"),
            },
        }

    def _build_knowledge_context(self, historical_knowledge: list[dict]) -> dict:
        if not historical_knowledge:
            return {"available": False, "sample_count": 0}
        return {
            "available": True,
            "sample_count": len(historical_knowledge),
            "range": {
                "first_index": historical_knowledge[0].get("candle_index"),
                "last_index": historical_knowledge[-1].get("candle_index"),
            },
        }

    def _build_prediction_context(self, historical_predictions: list[dict]) -> dict:
        if not historical_predictions:
            return {"available": False, "sample_count": 0}
        return {
            "available": True,
            "sample_count": len(historical_predictions),
            "range": {
                "first_index": historical_predictions[0].get("candle_index"),
                "last_index": historical_predictions[-1].get("candle_index"),
            },
        }
