"""
=====================================================
MODULE:     trade_package.py
PURPOSE:    Trade Package — structured report dari
            trade_snapshot cards.
OWNER:      PHASE-10 TRADE LAYER
INPUT:      List of trade_snapshot Cards
OUTPUT:     TradeReportPackage (dict)
DEPENDENCY: stlms.foundation.base_package (BasePackage)
ARCHITECTURE:
            Package mengagregasi multiple trade cards
            menjadi laporan terstruktur. Meringkas
            statistik entry/exit, P&L, win rate.
=====================================================
"""

from typing import Any
from ..core.utils import Card
from ..foundation.base_package import BasePackage


class TradePackage(BasePackage):
    """
    Membangun Trade Report Package dari trade_snapshot cards.

    Consumer:
        Dashboard, Recommendation Layer
    """

    def __init__(self):
        super().__init__("TRADE")

    def build(self, artifacts: list[Card]) -> dict:
        """
        Build structured report from trade_snapshot cards.

        Returns:
            TradeReportPackage dict with P&L and win rate summary.
        """
        if not artifacts:
            return {"layer": self.layer, "status": "EMPTY", "trades": 0}

        entries = [c for c in artifacts if c.payload.get("kind") == "ENTRY"]
        exits = [c for c in artifacts if c.payload.get("kind") == "EXIT"]

        wins = [c for c in exits if c.payload.get("result") == "WIN"]
        losses = [c for c in exits if c.payload.get("result") == "LOSS"]
        breakevens = [c for c in exits if c.payload.get("result") == "BREAKEVEN"]

        net_values = [c.payload.get("net", 0) for c in exits]
        total_net = sum(net_values)
        avg_net = total_net / len(net_values) if net_values else 0.0

        win_rate = len(wins) / len(exits) * 100 if exits else 0.0

        clones = set(c.payload.get("clone", "?") for c in artifacts)

        return {
            "layer": self.layer,
            "total_trades": len(exits),
            "entries": len(entries),
            "exits": len(exits),
            "wins": len(wins),
            "losses": len(losses),
            "breakevens": len(breakevens),
            "win_rate_pct": round(win_rate, 1),
            "total_net": round(total_net, 4),
            "avg_net": round(avg_net, 4),
            "clones": sorted(clones),
            "status": "OK",
        }

    def summary(self, report: dict) -> str:
        """Human-readable summary."""
        if report.get("status") == "EMPTY":
            return "Trade Report: No trades"

        return (
            f"Trade Report: {report.get('total_trades')} trades | "
            f"Win: {report.get('wins')} | Loss: {report.get('losses')} | "
            f"BE: {report.get('breakevens')} | "
            f"Win Rate: {report.get('win_rate_pct')}% | "
            f"Net: {report.get('total_net')}"
        )
