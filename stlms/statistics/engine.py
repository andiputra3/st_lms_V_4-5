"""
=====================================================
MODULE:     statistics_engine.py
PURPOSE:    Statistics — aggregate trade markers per clone.
            Sample-gated: CUKUP iff >= 30.
OWNER:      PHASE-10 STATISTICS LAYER
=====================================================
"""

from ..core.constants import SAMPLE_GATE


def compute_statistics(markers: list, clone_id: str) -> dict:
    """Compute per-clone statistics from trade markers."""
    exits = [m for m in markers if m.clone == clone_id and m.kind == "EXIT"]
    n = len(exits)
    
    if n == 0:
        return {"sample": 0, "status": "BELUM_CUKUP"}
    
    wins = sum(1 for m in exits if m.result == "WIN")
    net_total = sum(m.net for m in exits)
    gross_pos = sum(m.gross for m in exits if m.gross and m.gross > 0)
    gross_neg = sum(abs(m.gross) for m in exits if m.gross and m.gross < 0)
    mae_total = sum(abs(m.mae) for m in exits)
    mfe_total = sum(m.mfe for m in exits)
    fee_total = sum(m.fee for m in exits)
    wrong = sum(1 for m in exits if m.reason and "WRONG" in m.reason)
    
    return {
        "sample": n,
        "status": "CUKUP" if n >= SAMPLE_GATE else "BELUM_CUKUP",
        "wins": wins,
        "win_rate": round(wins / n * 100, 1) if n > 0 else None,
        "expectancy": round(net_total / n, 3) if n > 0 else None,
        "pf": round(gross_pos / gross_neg, 2) if gross_neg > 0 else None,
        "mae": round(mae_total / n, 3) if n > 0 else None,
        "mfe": round(mfe_total / n, 3) if n > 0 else None,
        "fee_drag": round(fee_total / n, 3) if n > 0 else None,
        "wrong_rate": round(wrong / n * 100, 1) if n > 0 else None,
    }
