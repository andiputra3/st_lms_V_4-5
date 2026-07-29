"""
=====================================================
MODULE:     statistics/domains/clone_stats.py
PURPOSE:    Clone Statistics — per-clone metrics,
            observation-to-entry ratio,
            no-entry reason distribution.
OWNER:      STATISTICS LAYER — CLONE DOMAIN
=====================================================
"""

from typing import Optional
from ...clone.engine import TradeMarker


class CloneStatistics:
    """
    Compute clone-level statistics from TradeMarker data.

    Metrics:
        - Per-clone performance (win_rate, expectancy, pf, etc.)
        - Observation-to-entry ratio
        - No-entry reason distribution
    """

    def compute(self,
                markers: Optional[list[TradeMarker]] = None,
                observations: Optional[list[dict]] = None) -> dict:
        result: dict = {
            "per_clone": {},
            "observation_to_entry_ratio": 0.0,
            "no_entry_reasons": {},
            "total_entries": 0,
            "total_exits": 0,
            "total_observations": 0,
        }

        if not markers:
            return result

        entries = [m for m in markers if m.kind == "ENTRY"]
        exits = [m for m in markers if m.kind == "EXIT"]
        result["total_entries"] = len(entries)
        result["total_exits"] = len(exits)

        for m in exits:
            clone_id = m.clone
            if clone_id not in result["per_clone"]:
                result["per_clone"][clone_id] = {
                    "exits": 0, "wins": 0, "losses": 0,
                    "win_rate": 0.0, "expectancy": 0.0,
                    "pf": 0.0, "mae_avg": 0.0, "mfe_avg": 0.0,
                    "fee_drag": 0.0, "wrong_rate": 0.0,
                }
            c = result["per_clone"][clone_id]
            c["exits"] += 1
            if m.result == "WIN":
                c["wins"] += 1
            elif m.result == "LOSS":
                c["losses"] += 1

        for clone_id, c in result["per_clone"].items():
            n = c["exits"]
            if n > 0:
                c["win_rate"] = round(c["wins"] / n * 100, 1)
                clone_exits = [m for m in exits if m.clone == clone_id]
                nets = [m.net for m in clone_exits if m.net is not None]
                gross_pos = sum(
                    m.gross for m in clone_exits
                    if m.gross is not None and m.gross > 0
                )
                gross_neg = sum(
                    abs(m.gross) for m in clone_exits
                    if m.gross is not None and m.gross < 0
                )
                maes = [abs(m.mae) for m in clone_exits]
                mfes = [m.mfe for m in clone_exits]
                fees = [m.fee for m in clone_exits]
                wrongs = sum(
                    1 for m in clone_exits
                    if m.reason and "WRONG" in m.reason
                )

                c["expectancy"] = round(sum(nets) / n, 3) if nets else 0.0
                c["pf"] = round(gross_pos / gross_neg, 2) if gross_neg > 0 else 0.0
                c["mae_avg"] = round(sum(maes) / n, 3) if maes else 0.0
                c["mfe_avg"] = round(sum(mfes) / n, 3) if mfes else 0.0
                c["fee_drag"] = round(sum(fees) / n, 3) if fees else 0.0
                c["wrong_rate"] = round(wrongs / n * 100, 1)

        if observations:
            result["total_observations"] = len(observations)
            if len(entries) > 0:
                result["observation_to_entry_ratio"] = round(
                    len(observations) / len(entries), 2
                )

            for obs in observations:
                reason = obs.get("no_entry_reason")
                if reason:
                    result["no_entry_reasons"][reason] = \
                        result["no_entry_reasons"].get(reason, 0) + 1

        return result
