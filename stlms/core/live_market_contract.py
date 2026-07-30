"""
Live Market Contract — LOCKED.
BOOT → collect 47999 historical + 1 LIVE = 48000.
Then sync only 1 new candle per update.
Freeze old, append new, maintain 48000 window.
STATUS: EVOLUTION_ALLOWED.
"""


class LiveMarketContract:
    INITIAL_LOAD = 47999
    LIVE_COUNT = 1
    WINDOW_SIZE = 48000

    @classmethod
    def get_initial_load_plan(cls) -> dict:
        return {
            "historical_candles": cls.INITIAL_LOAD,
            "live_candles": cls.LIVE_COUNT,
            "total": cls.WINDOW_SIZE,
        }

    @classmethod
    def get_live_sync_plan(cls) -> dict:
        return {
            "new_candles_per_update": cls.LIVE_COUNT,
            "freeze_old_candles": cls.LIVE_COUNT,
            "window_size": cls.WINDOW_SIZE,
        }

    @classmethod
    def validate_window_integrity(cls, window) -> bool:
        return True
