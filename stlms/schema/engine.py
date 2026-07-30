"""
=====================================================
MODULE:     schema_engine.py
PURPOSE:    Trading Schema — 41 schemas, 5 categories.
            Market condition -> trading behavior mapping.
OWNER:      PHASE-13 TRADING SCHEMA LAYER
=====================================================
"""

# Market schemas (10)
MARKET_SCHEMAS = {
    "TREND": {"condition": "stDir != 0, cage = NONE", "active": ["LONG", "SHORT"]},
    "SIDEWAY": {"condition": "cage.status != NONE", "active": ["GRID"]},
    "RANGE": {"condition": "wave = CONFIRMED_RANGE/SIDEWAY", "active": ["GRID"]},
    "CHAOS": {"condition": "wave = CHAOS", "active": []},
    "COMPRESSION": {"condition": "cage = VALID_COMPRESSION", "active": ["GRID"]},
    "EXPANSION": {"condition": "cage = LOOSE_SIDEWAY", "active": ["GRID"]},
    "BREAKOUT": {"condition": "cage.breakout != NONE", "active": ["LONG", "SHORT"]},
    "REVERSAL": {"condition": "wave = REVERSAL_UP/DOWN", "active": ["LONG", "SHORT"]},
    "EXHAUSTION": {"condition": "wave = EXHAUSTION_UP/DOWN", "active": []},
    "WARMUP": {"condition": "point_status = WARMUP", "active": []},
}

# Entry schemas (11)
ENTRY_SCHEMAS = {
    "LONG_CONTINUATION": {"confidence": "HIGH", "risk": "LOW"},
    "LONG_PULLBACK": {"confidence": "MEDIUM", "risk": "MEDIUM"},
    "LONG_BREAKOUT": {"confidence": "MEDIUM", "risk": "HIGH"},
    "LONG_REVERSAL": {"confidence": "LOW", "risk": "HIGH"},
    "SHORT_CONTINUATION": {"confidence": "HIGH", "risk": "LOW"},
    "SHORT_PULLBACK": {"confidence": "MEDIUM", "risk": "MEDIUM"},
    "SHORT_BREAKOUT": {"confidence": "MEDIUM", "risk": "HIGH"},
    "SHORT_REVERSAL": {"confidence": "LOW", "risk": "HIGH"},
    "GRID_COMPRESSION": {"confidence": "HIGH", "risk": "LOW"},
    "GRID_RANGE": {"confidence": "MEDIUM", "risk": "MEDIUM"},
    "GRID_EXPANSION": {"confidence": "LOW", "risk": "HIGH"},
}

EXIT_SCHEMAS = {
    "TP1_FAST": {"type": "TAKE_PROFIT", "risk": "LOW", "target_pct": 1.0},
    "TP2_STRUCTURE": {"type": "TAKE_PROFIT", "risk": "MEDIUM", "target_pct": 2.0},
    "TP3_EXTENDED": {"type": "TAKE_PROFIT", "risk": "HIGH", "target_pct": 3.0},
    "SL_ATR": {"type": "STOP_LOSS", "risk": "LOW", "multiplier": 1.5},
    "SL_STRUCTURE": {"type": "STOP_LOSS", "risk": "MEDIUM", "multiplier": 2.0},
    "SL_TRAILING": {"type": "STOP_LOSS", "risk": "LOW", "trail_pct": 0.5},
    "BE_CROSS": {"type": "BREAKEVEN", "risk": "LOW"},
    "TIME_EXIT": {"type": "TIME_BASED", "risk": "MEDIUM", "max_bars": 20},
    "REVERSAL_EXIT": {"type": "SIGNAL_BASED", "risk": "MEDIUM"},
    "VOLATILITY_EXIT": {"type": "VOLATILITY_BASED", "risk": "HIGH"},
}

RISK_SCHEMAS = {
    "CONSERVATIVE": {"position_pct": 1.0, "max_drawdown": 5.0, "risk_per_trade": 0.5},
    "MODERATE": {"position_pct": 2.0, "max_drawdown": 10.0, "risk_per_trade": 1.0},
    "AGGRESSIVE": {"position_pct": 5.0, "max_drawdown": 20.0, "risk_per_trade": 2.0},
    "SCALPING": {"position_pct": 0.5, "max_drawdown": 2.0, "risk_per_trade": 0.25},
    "SWING": {"position_pct": 3.0, "max_drawdown": 15.0, "risk_per_trade": 1.5},
    "POSITION": {"position_pct": 7.0, "max_drawdown": 25.0, "risk_per_trade": 3.0},
    "ADAPTIVE": {"position_pct": 2.0, "max_drawdown": 10.0, "risk_per_trade": 1.0},
    "HEDGED": {"position_pct": 4.0, "max_drawdown": 8.0, "risk_per_trade": 1.5},
    "GRID_RISK": {"position_pct": 1.5, "max_drawdown": 7.0, "risk_per_trade": 0.75},
    "MOMENTUM": {"position_pct": 3.0, "max_drawdown": 12.0, "risk_per_trade": 2.0},
}


class SchemaEngine:
    """Trading Schema — menentukan schema berdasarkan market condition."""
    
    def select_market_schema(self, cage_status: str, wave_structure: str,
                             st_dir: int, breakout: str, point_status: str) -> str:
        if point_status == "WARMUP":
            return "WARMUP"
        if wave_structure in ("EXHAUSTION_UP", "EXHAUSTION_DOWN"):
            return "EXHAUSTION"
        if wave_structure in ("REVERSAL_UP", "REVERSAL_DOWN"):
            return "REVERSAL"
        if breakout != "NONE":
            return "BREAKOUT"
        if cage_status == "VALID_COMPRESSION":
            return "COMPRESSION"
        if cage_status == "LOOSE_SIDEWAY":
            return "EXPANSION"
        if cage_status != "NONE":
            return "SIDEWAY"
        if wave_structure == "CHAOS":
            return "CHAOS"
        if wave_structure in ("CONFIRMED_RANGE", "SIDEWAY"):
            return "RANGE"
        return "TREND"
    
    def select_entry_schema(self, market_schema: str, st_dir: int,
                            prediction: dict) -> str:
        bias = prediction.get("dominant_bias", "NEUTRAL")
        
        if market_schema in ("COMPRESSION", "SIDEWAY", "RANGE"):
            if market_schema == "COMPRESSION":
                return "GRID_COMPRESSION"
            return "GRID_RANGE" if market_schema == "RANGE" else "GRID_COMPRESSION"
        
        if market_schema == "BREAKOUT":
            return "LONG_BREAKOUT" if st_dir == 1 else "SHORT_BREAKOUT"
        
        if market_schema == "REVERSAL":
            return "LONG_REVERSAL" if st_dir == 1 else "SHORT_REVERSAL"
        
        if market_schema == "TREND":
            if st_dir == 1:
                return "LONG_CONTINUATION" if bias == "BULLISH" else "LONG_PULLBACK"
            return "SHORT_CONTINUATION" if bias == "BEARISH" else "SHORT_PULLBACK"
        
        return "WAIT"
    
    def get_active_clones(self, market_schema: str) -> list[str]:
        return MARKET_SCHEMAS.get(market_schema, {}).get("active", [])

    def select_exit_schema(self, entry_schema: str, market_schema: str,
                           atr: float, price: float) -> str:
        if market_schema in ("COMPRESSION", "RANGE"):
            return "TP1_FAST"
        if "BREAKOUT" in entry_schema:
            return "TP2_STRUCTURE"
        if "REVERSAL" in entry_schema:
            return "SL_STRUCTURE"
        if "CONTINUATION" in entry_schema:
            return "TP3_EXTENDED"
        return "SL_ATR"

    def select_risk_schema(self, market_schema: str, prediction: dict,
                           win_rate: float = 0) -> str:
        score = prediction.get("intelligence_score", 5000)
        bias = prediction.get("dominant_bias", "NEUTRAL")

        if market_schema in ("CHAOS", "EXHAUSTION", "WARMUP"):
            return "CONSERVATIVE"
        if market_schema in ("COMPRESSION", "RANGE"):
            return "GRID_RISK"
        if win_rate > 65 and score > 7000:
            return "AGGRESSIVE"
        if win_rate > 55 and score > 6000:
            return "MODERATE"
        if bias == "NEUTRAL":
            return "ADAPTIVE"
        return "CONSERVATIVE"
