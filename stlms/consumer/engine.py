"""
=====================================================
MODULE:     consumer_engine.py
PURPOSE:    Consumer Layer — fund eval, veto, intent, CSV.
            Live adapter DISABLED default.
OWNER:      PHASE-17 MARKET CONSUMER
=====================================================
"""

import csv
import io
from ..core.constants import ASSETS


class ConsumerEngine:
    """Consumer — downstream API untuk trading intent."""
    
    def __init__(self):
        self.live_enabled = False
    
    def fund_eval(self, confidence: float, capital: float = 100.0) -> dict:
        conf_pct = confidence / 10000
        size = min(capital * 0.10 * conf_pct, capital * 0.10)
        return {
            "allowed": True,
            "position_size": round(size, 2),
            "leverage": 3,
            "capital": capital,
        }
    
    def veto_gate(self, confidence: float, data_status: str,
                  global_ok: bool = True) -> dict:
        checks = {
            "confidence_ok": confidence >= 3000,
            "data_ok": data_status in ("ok", "FINAL", "VALID"),
            "global_ok": global_ok,
        }
        failed = [k for k, v in checks.items() if not v]
        return {
            "decision": "ALLOW" if not failed else "REJECT",
            "checks": checks,
            "failed": failed,
        }
    
    def intent_builder(self, symbol: str, phase: str, confidence: float,
                       close: float, auth: dict) -> dict:
        if auth["decision"] != "ALLOW":
            return {"status": "REJECTED", "reason": auth["failed"]}
        
        if "SIDEWAY" in phase or "COMPRESSION" in phase:
            return {"status": "GRID_INTENT", "side": "GRID"}
        
        side = "LONG" if confidence > 5000 else "SHORT"
        asset = ASSETS.get(symbol, ASSETS["BTCUSDT"])
        prec = asset["prec"]
        
        return {
            "status": "READY",
            "side": side,
            "entry": round(close, prec),
        }
    
    def export_csv(self, markers: list) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ts", "clone", "side", "kind", "reason", "entry", "exit", "net", "result"])
        for m in markers:
            writer.writerow([m.ts, m.clone, m.side, m.kind, m.reason,
                           m.entry, m.exit, m.net, m.result])
        return output.getvalue()
