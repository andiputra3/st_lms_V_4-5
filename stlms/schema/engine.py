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
