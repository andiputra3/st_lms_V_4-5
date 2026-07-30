"""
Live Research Window Contract — LOCKED.
48000 = Live Research Window. Market being actively researched.
SQLite stores millions of observations (historical archive).
48000 is just the active window being studied RIGHT NOW.
STATUS: EVOLUTION_ALLOWED.
"""


class LiveResearchWindow:
    def __init__(self, window_size=48000):
        self.window_size = window_size
        self._window = []
        self._total_archived = 0
        self._archive_log = []

    def add_observation(self, observation) -> int:
        self._window.append(observation)
        if len(self._window) > self.window_size:
            self._archive_one()
        return len(self._window)

    def get_active_window(self) -> list:
        return list(self._window)

    def get_observation(self, index) -> dict:
        if 0 <= index < len(self._window):
            return self._window[index]
        return {}

    def is_window_full(self) -> bool:
        return len(self._window) >= self.window_size

    def archive_window(self) -> dict:
        count = len(self._window)
        self._total_archived += count
        self._archive_log.append({"count": count, "remaining": 0})
        self._window.clear()
        return {"archived": count, "total_archived": self._total_archived}

    def get_archive_stats(self) -> dict:
        return {
            "total_archived": self._total_archived,
            "archive_log": self._archive_log,
            "window_size": self.window_size,
            "current_window": len(self._window),
        }

    def get_total_observations_ever(self) -> int:
        return self._total_archived + len(self._window)

    def _archive_one(self):
        self._total_archived += 1
        self._window.pop(0)
