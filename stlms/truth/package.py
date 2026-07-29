"""
=====================================================
MODULE:     truth_package.py
PURPOSE:    Truth Package — structured report dari SP.
OWNER:      PHASE-04 TRUTH LAYER
=====================================================
"""

from ..core.utils import Card
from ..foundation.base_package import BasePackage


class TruthPackage(BasePackage):
    """Truth Report Package — agregasi SP menjadi laporan."""
    
    def __init__(self):
        super().__init__("TRUTH")
    
    def build(self, artifacts: list[Card]) -> dict:
        if not artifacts:
            return {"layer": self.layer, "status": "EMPTY", "points": 0}
        
        last = artifacts[-1].payload
        valid = [a for a in artifacts if a.payload.get("point_status") == "VALID"]
        flips = [a for a in artifacts if a.payload.get("flip")]
        
        return {
            "layer": self.layer,
            "points": len(artifacts),
            "valid_points": len(valid),
            "warmup_points": len(artifacts) - len(valid),
            "flips": len(flips),
            "current": {
                "st": last.get("st"),
                "st_dir": last.get("st_dir"),
                "st_color": last.get("st_color"),
                "atr": last.get("atr"),
                "ema": last.get("ema"),
                "rsi": last.get("rsi"),
                "wpr": last.get("wpr"),
                "macd_hist": last.get("macd_hist"),
                "dist_atr": last.get("dist_atr"),
                "vol_delta": last.get("vol_delta"),
                "point_status": last.get("point_status"),
            },
            "oi_summary": {
                "current": last.get("oi_value"),
                "delta": last.get("oi_delta"),
            },
            "status": "OK",
        }
    
    def summary(self, report: dict) -> str:
        if report.get("status") == "EMPTY":
            return "Truth Report: No data"
        c = report.get("current", {})
        return (
            f"Truth Report: {report.get('points')} SP | "
            f"ST={c.get('st')} dir={c.get('st_dir')} color={c.get('st_color')} | "
            f"ATR={c.get('atr')} dist={c.get('dist_atr')} | "
            f"RSI={c.get('rsi')} W%R={c.get('wpr')} | "
            f"Flips={report.get('flips')}"
        )
