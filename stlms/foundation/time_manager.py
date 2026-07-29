"""
ST-LMS v3 — Time Manager
Foundation Core — Phase 1

WIB timezone, timestamp utilities.
"""

from datetime import datetime, timezone, timedelta
from ..core.constants import WIB_OFFSET_SECONDS, MS_PER_MINUTE

WIB = timezone(timedelta(seconds=WIB_OFFSET_SECONDS))

class TimeManager:
    @staticmethod
    def now_ms() -> int:
        return int(datetime.now(WIB).timestamp() * 1000)

    @staticmethod
    def wib_iso(ts_ms: int) -> str:
        dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=WIB)
        return dt.isoformat()

    @staticmethod
    def wib_ymd(ts_ms: int) -> str:
        dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=WIB)
        return dt.strftime("%Y%m%d")

    @staticmethod
    def wib_hhmm(ts_ms: int) -> str:
        dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=WIB)
        return dt.strftime("%H%M")

    @staticmethod
    def candle_timestamp(base_ts: int, candle_index: int, interval_ms: int = MS_PER_MINUTE) -> int:
        return base_ts + candle_index * interval_ms

    @staticmethod
    def is_valid_sequence(timestamps: list[int], interval_ms: int = MS_PER_MINUTE) -> list[int]:
        gaps = []
        for i in range(1, len(timestamps)):
            if timestamps[i] - timestamps[i-1] > interval_ms:
                gaps.append(timestamps[i])
        return gaps
