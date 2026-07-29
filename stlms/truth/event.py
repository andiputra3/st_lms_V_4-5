"""
=====================================================
MODULE:     truth_event.py
PURPOSE:    Market Event — event recording for Truth
            Layer anomaly and mutation events.
=====================================================
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EventType(str, Enum):
    PRICE_EXPLOSION = "PRICE_EXPLOSION"
    VOLUME_EXPLOSION = "VOLUME_EXPLOSION"
    OI_EXPLOSION = "OI_EXPLOSION"
    TREND_FLIP = "TREND_FLIP"
    STRUCTURE_MUTATION = "STRUCTURE_MUTATION"
    WAVE_MUTATION = "WAVE_MUTATION"
    DISTANCE_MUTATION = "DISTANCE_MUTATION"
    PREDICTION_MUTATION = "PREDICTION_MUTATION"
    RECOMMENDATION_MUTATION = "RECOMMENDATION_MUTATION"
    MARKET_MUTATION = "MARKET_MUTATION"
    CLONE_MUTATION = "CLONE_MUTATION"
    STATISTICS_MUTATION = "STATISTICS_MUTATION"
    GAP_DETECTION = "GAP_DETECTION"
    WARMUP_COMPLETE = "WARMUP_COMPLETE"
    EXTREME_RSI = "EXTREME_RSI"
    EXTREME_WPR = "EXTREME_WPR"
    MACD_CROSSOVER = "MACD_CROSSOVER"
    VOLUME_DIVERGENCE = "VOLUME_DIVERGENCE"


@dataclass
class MarketEvent:
    ts: int
    event_type: EventType
    severity: str
    detail: str
    metadata: dict = field(default_factory=dict)


class MarketEventRecorder:
    """
    Records MarketEvents from TruthPoint data.
    Supports threshold-based detection for common events.
    """

    def __init__(self):
        self._events: list[MarketEvent] = []

    @property
    def events(self) -> list[MarketEvent]:
        return list(self._events)

    def record(self, ts: int, event_type: EventType, severity: str,
               detail: str, metadata: Optional[dict] = None) -> MarketEvent:
        event = MarketEvent(
            ts=ts,
            event_type=event_type,
            severity=severity,
            detail=detail,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def record_if(self, ts: int, event_type: EventType, severity: str,
                  detail: str, condition: bool,
                  metadata: Optional[dict] = None) -> Optional[MarketEvent]:
        if not condition:
            return None
        return self.record(ts, event_type, severity, detail, metadata)

    def to_dict_list(self) -> list[dict]:
        return [
            {
                "ts": e.ts,
                "event_type": e.event_type.value,
                "severity": e.severity,
                "detail": e.detail,
                "metadata": e.metadata,
            }
            for e in self._events
        ]

    def query(self, event_type: Optional[EventType] = None,
              start: Optional[int] = None,
              end: Optional[int] = None) -> list[MarketEvent]:
        result = self._events
        if event_type is not None:
            result = [e for e in result if e.event_type == event_type]
        if start is not None:
            result = [e for e in result if e.ts >= start]
        if end is not None:
            result = [e for e in result if e.ts <= end]
        return result

    def clear(self):
        self._events.clear()
