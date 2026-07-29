"""
=====================================================
MODULE:     truth_timeline.py
PURPOSE:    Truth Timeline — time-series queries over
            TruthPoint collections for 15 timeline types.
=====================================================
"""

from typing import Optional

from ..truth.point import TruthPoint


class TruthTimeline:
    """
    Query interface for 15 timeline types from TruthPoint collections.

    Each method accepts (start, end) as epoch ms and returns
    list[dict] with at minimum {'ts', 'value'} entries.
    """

    def __init__(self, points: list[TruthPoint]):
        self._points = sorted(points, key=lambda p: p.ts)
        self._clone_points: dict[str, list[TruthPoint]] = {}
        self._event_log: list[dict] = []
        self._mutation_log: list[dict] = []
        self._snapshot_log: list[dict] = []

    @property
    def points(self) -> list[TruthPoint]:
        return list(self._points)

    def _filter_range(self, start: Optional[int] = None,
                      end: Optional[int] = None) -> list[TruthPoint]:
        if not self._points:
            return []
        result = self._points
        if start is not None:
            result = [p for p in result if p.ts >= start]
        if end is not None:
            result = [p for p in result if p.ts <= end]
        return result

    def _safe(self, val, default=None):
        return val if val is not None else default

    def register_clone(self, clone_id: str, points: list[TruthPoint]):
        self._clone_points[clone_id] = sorted(points, key=lambda p: p.ts)

    def register_events(self, events: list[dict]):
        self._event_log = events

    def register_mutations(self, mutations: list[dict]):
        self._mutation_log = mutations

    def register_snapshots(self, snapshots: list[dict]):
        self._snapshot_log = snapshots

    # ── 15 Timeline Methods ──────────────────────────────────

    def price(self, start: Optional[int] = None,
              end: Optional[int] = None) -> list[dict]:
        return [{"ts": p.ts, "value": p.close}
                for p in self._filter_range(start, end)]

    def volume(self, start: Optional[int] = None,
               end: Optional[int] = None) -> list[dict]:
        return [{"ts": p.ts, "value": p.vol_delta}
                for p in self._filter_range(start, end)]

    def oi(self, start: Optional[int] = None,
           end: Optional[int] = None) -> list[dict]:
        return [{"ts": p.ts, "value": self._safe(p.oi_value, 0.0)}
                for p in self._filter_range(start, end)]

    def rsi(self, start: Optional[int] = None,
            end: Optional[int] = None) -> list[dict]:
        result = []
        for p in self._filter_range(start, end):
            if p.rsi is not None:
                result.append({"ts": p.ts, "value": p.rsi})
        return result

    def macd(self, start: Optional[int] = None,
             end: Optional[int] = None) -> list[dict]:
        result = []
        for p in self._filter_range(start, end):
            entry = {"ts": p.ts, "value": self._safe(p.macd, 0.0)}
            entry["macd_signal"] = self._safe(p.macd_signal, 0.0)
            entry["macd_hist"] = self._safe(p.macd_hist, 0.0)
            result.append(entry)
        return result

    def wpr(self, start: Optional[int] = None,
            end: Optional[int] = None) -> list[dict]:
        result = []
        for p in self._filter_range(start, end):
            if p.wpr is not None:
                result.append({"ts": p.ts, "value": p.wpr})
        return result

    def distance(self, start: Optional[int] = None,
                 end: Optional[int] = None) -> list[dict]:
        result = []
        for p in self._filter_range(start, end):
            entry = {"ts": p.ts, "value": self._safe(p.dist, 0.0)}
            entry["dist_atr"] = self._safe(p.dist_atr, 0.0)
            result.append(entry)
        return result

    def structure(self, start: Optional[int] = None,
                  end: Optional[int] = None) -> list[dict]:
        return [{"ts": p.ts, "st": p.st, "st_dir": p.st_dir,
                 "st_color": p.st_color, "st_canon": p.st_canon,
                 "flip": p.flip}
                for p in self._filter_range(start, end)]

    def clone(self, clone_id: str, start: Optional[int] = None,
              end: Optional[int] = None) -> list[dict]:
        pts = self._clone_points.get(clone_id, [])
        if start is not None:
            pts = [p for p in pts if p.ts >= start]
        if end is not None:
            pts = [p for p in pts if p.ts <= end]
        return [{"ts": p.ts, "st": p.st, "st_dir": p.st_dir,
                 "st_color": p.st_color, "close": p.close,
                 "atr": p.atr, "rsi": p.rsi, "wpr": p.wpr,
                 "dist_atr": p.dist_atr}
                for p in pts]

    def statistics(self, start: Optional[int] = None,
                   end: Optional[int] = None) -> list[dict]:
        return [e for e in self._snapshot_log
                if (start is None or e.get("ts", 0) >= start)
                and (end is None or e.get("ts", 0) <= end)]

    def prediction(self, start: Optional[int] = None,
                   end: Optional[int] = None) -> list[dict]:
        result = []
        for p in self._filter_range(start, end):
            result.append({
                "ts": p.ts, "close": p.close, "st": p.st,
                "st_dir": p.st_dir, "rsi": p.rsi, "wpr": p.wpr,
                "macd_hist": self._safe(p.macd_hist, 0.0),
                "dist_atr": self._safe(p.dist_atr, 0.0),
                "vol_delta": p.vol_delta,
            })
        return result

    def recommendation(self, start: Optional[int] = None,
                       end: Optional[int] = None) -> list[dict]:
        result = []
        for p in self._filter_range(start, end):
            result.append({
                "ts": p.ts, "close": p.close, "st": p.st,
                "st_dir": p.st_dir, "st_color": p.st_color,
                "flip": p.flip, "point_status": p.point_status.value,
                "rsi": p.rsi, "wpr": p.wpr,
            })
        return result

    def events(self, start: Optional[int] = None,
               end: Optional[int] = None) -> list[dict]:
        return [e for e in self._event_log
                if (start is None or e.get("ts", 0) >= start)
                and (end is None or e.get("ts", 0) <= end)]

    def mutation(self, start: Optional[int] = None,
                 end: Optional[int] = None) -> list[dict]:
        return [m for m in self._mutation_log
                if (start is None or m.get("ts", 0) >= start)
                and (end is None or m.get("ts", 0) <= end)]

    def snapshot(self, start: Optional[int] = None,
                 end: Optional[int] = None) -> list[dict]:
        return [{"ts": p.ts, "close": p.close, "st": p.st,
                 "st_dir": p.st_dir, "st_color": p.st_color,
                 "atr": p.atr, "ema": p.ema, "rsi": p.rsi,
                 "wpr": p.wpr, "macd_hist": self._safe(p.macd_hist, 0.0),
                 "dist_atr": self._safe(p.dist_atr, 0.0),
                 "flip": p.flip, "point_status": p.point_status.value,
                 "oi_value": p.oi_value, "oi_delta": p.oi_delta,
                 "vol_delta": p.vol_delta}
                for p in self._filter_range(start, end)]
