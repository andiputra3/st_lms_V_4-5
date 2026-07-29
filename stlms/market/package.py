"""
=====================================================
MODULE:     market_package.py
PURPOSE:    Market Package — structured report dari
            market_snapshot cards.
OWNER:      PHASE-02 MARKET ARTIFACT
INPUT:      List of market_snapshot Cards
OUTPUT:     MarketReportPackage (dict)
DEPENDENCY: stlms.foundation.base_package (BasePackage)
ARCHITECTURE:
            Package mengagregasi multiple cards menjadi
            laporan terstruktur. Tidak melakukan komputasi baru.
            Hanya membaca dan meringkas.
=====================================================
"""

from typing import Any
from ..core.utils import Card
from ..foundation.base_package import BasePackage


class MarketPackage(BasePackage):
    """
    Membangun Market Report Package dari market_snapshot cards.
    
    Consumer:
        Dashboard, Recommendation Layer (Phase-15)
    """
    
    def __init__(self):
        super().__init__("MARKET")
    
    def build(self, artifacts: list[Card]) -> dict:
        """
        Bangun structured report dari artifacts.
        
        Returns:
            MarketReportPackage dict dengan summary statistik.
        """
        if not artifacts:
            return {"layer": self.layer, "status": "EMPTY", "candles": 0}
        
        prices = [c.payload.get("close", 0) for c in artifacts]
        volumes = [c.payload.get("volume", 0) for c in artifacts]
        oi_values = [c.payload.get("oi_value") for c in artifacts if c.payload.get("oi_value")]
        gaps = sum(1 for c in artifacts if c.payload.get("gap_flag"))
        
        return {
            "layer": self.layer,
            "symbol": artifacts[0].payload.get("symbol", "?"),
            "timeframe": artifacts[0].payload.get("timeframe", "?"),
            "candles": len(artifacts),
            "gaps": gaps,
            "oi_slots": len(set(
                c.payload.get("oi_value") for c in artifacts
                if c.payload.get("oi_value")
            )),
            "price_summary": {
                "open": artifacts[0].payload.get("open"),
                "close": artifacts[-1].payload.get("close"),
                "high": max(prices),
                "low": min(prices),
            },
            "volume_summary": {
                "total": sum(volumes),
                "average": sum(volumes) / len(volumes) if volumes else 0,
            },
            "data_quality": {
                "gaps": gaps,
                "gap_pct": round(gaps / len(artifacts) * 100, 1),
            },
            "status": "OK",
        }
    
    def summary(self, report: dict) -> str:
        """Human-readable summary."""
        if report.get("status") == "EMPTY":
            return "Market Report: No data"
        ps = report.get("price_summary", {})
        dq = report.get("data_quality", {})
        return (
            f"Market Report: {report.get('symbol')} {report.get('timeframe')} | "
            f"{report.get('candles')} candles | "
            f"O:{ps.get('open')} H:{ps.get('high')} L:{ps.get('low')} C:{ps.get('close')} | "
            f"Gaps: {dq.get('gaps')} ({dq.get('gap_pct')}%)"
        )
