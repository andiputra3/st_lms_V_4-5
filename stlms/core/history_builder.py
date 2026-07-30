"""
Tahap 14 · Market History Builder
Tugas: Mencatat perubahan dari seluruh layer.
Deteksi: Truth berubah, Wave berubah, Prediction berubah, DNA berubah, Reliability berubah.
Output: Timeline Artifact
"""
from dataclasses import dataclass, field
import time


@dataclass
class TimelineEntry:
    timeline_id: str
    observation_index: int
    change_type: str  # TRUTH_CHANGE, WAVE_CHANGE, PREDICTION_CHANGE, DNA_CHANGE, RELIABILITY_CHANGE, STRUCTURE_CHANGE
    previous_value: str
    new_value: str
    timestamp: int


class MarketHistoryBuilder:
    """Mencatat perubahan seluruh layer menjadi timeline."""

    def __init__(self, timeline_id: str | None = None):
        self._timeline_id = timeline_id or f"tl-{int(time.time())}"
        self._entries: list[TimelineEntry] = []

    def detect_changes(self, prev_observation: dict,
                       current_observation: dict) -> list[TimelineEntry]:
        entries: list[TimelineEntry] = []
        if not prev_observation or not current_observation:
            return entries

        for key, prev_val in prev_observation.items():
            current_val = current_observation.get(key)
            if prev_val != current_val:
                change_type = self._classify_change(key)
                entries.append(TimelineEntry(
                    timeline_id=self._timeline_id,
                    observation_index=current_observation.get("candle_index", 0),
                    change_type=change_type,
                    previous_value=str(prev_val),
                    new_value=str(current_val),
                    timestamp=int(time.time() * 1000),
                ))

        self._entries.extend(entries)
        return entries

    def build_timeline(self,
                       observations: list[dict]) -> list[TimelineEntry]:
        entries: list[TimelineEntry] = []
        for i in range(1, len(observations)):
            entries.extend(
                self.detect_changes(observations[i - 1], observations[i])
            )
        return entries

    def get_timeline_summary(self) -> dict:
        counts: dict[str, int] = {}
        for entry in self._entries:
            counts[entry.change_type] = counts.get(entry.change_type, 0) + 1
        return {
            "timeline_id": self._timeline_id,
            "total_entries": len(self._entries),
            "change_counts": counts,
        }

    def _classify_change(self, key: str) -> str:
        key_upper = key.upper()
        if "TRUTH" in key_upper:
            return "TRUTH_CHANGE"
        if "WAVE" in key_upper:
            return "WAVE_CHANGE"
        if "PREDICTION" in key_upper:
            return "PREDICTION_CHANGE"
        if "DNA" in key_upper:
            return "DNA_CHANGE"
        if "RELIABILITY" in key_upper:
            return "RELIABILITY_CHANGE"
        if "STRUCTURE" in key_upper:
            return "STRUCTURE_CHANGE"
        return "STRUCTURE_CHANGE"
