"""
=====================================================
MODULE:     clone_engine.py
PURPOSE:    Clone Engine — LONG, SHORT, GRID trading logic.
            Entry conjunction, exit priority, position mgmt.
            PER-CLONE: 3x isolated sub-ledgers.
OWNER:      PHASE-09 CLONE LAYER, PHASE-10 TRADE LAYER,
            PHASE-11 POSITION LAYER, PHASE-14 TRADING TRUTH
ARCHITECTURE:
            Clone = runtime entity dengan ledger sendiri.
            Card Sharing: Truth/Structure/Evidence 1x -> 3 clone.
            1 candle = 3 knowledge (LONG + SHORT + GRID).
            W%R/MACD/RSI = EXIT ONLY (forbidden for entry).
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional
from ..core.types import TradeKind, TradeSide, TradeResult, PositionStatus
from ..core.constants import (
    ENTRY_OFFSET_BASE_K, ENTRY_OFFSET_MIN_ATR, ENTRY_OFFSET_MAX_CAP_PCT,
    WPR_VELOCITY_DEADZONE, WRONG_ENTRY_PCT, GRID_MIN_NET_PCT_OF_FILL,
    GRID_BUY_ZONE_MAX, GRID_SELL_ZONE_MIN, GRID_MAX_FILLS_PER_SIDE,
    TP_ATR_MULT, TIME_EXIT_CANDLES, REQUIRED_MOVE
)


@dataclass
class Position:
    side: str  # LONG / SHORT / GRID
    entry_price: float
    sl: float
    tp: float
    mae: float = 0.0
    mfe: float = 0.0
    hold_c: int = 0
    status: str = "OPEN"


@dataclass
class CloneLedger:
    clone_id: str  # LONG / SHORT / GRID
    bias: str
    positions: list[Position] = field(default_factory=list)
    equity: list[float] = field(default_factory=list)
    capital: float = 100.0
    last_obs: Optional[dict] = None
    
    def __post_init__(self):
        if not self.equity:
            self.equity = [self.capital]


@dataclass
class TradeMarker:
    ts: int
    clone: str
    side: str
    kind: str  # ENTRY / EXIT
    reason: str
    entry: float
    exit: Optional[float] = None
    gross: Optional[float] = None
    fee: float = 0.0
    slip: float = 0.05
    net: Optional[float] = None
    result: Optional[str] = None
    mae: float = 0.0
    mfe: float = 0.0
    hold: int = 0


class CloneEngine:
    """
    Clone trading engine — LONG, SHORT, GRID.
    
    Entry Conjunction (LONG):
        stDir=+1 AND ema_slope>0 AND vol_delta>0 AND corridor AND fee_safe AND no_position
    
    Entry Conjunction (SHORT):
        stDir=-1 AND ema_slope<0 AND vol_delta<0 AND corridor AND fee_safe AND no_position
    
    Entry Conjunction (GRID):
        cage_valid AND width>=3*required AND breakout=NONE AND pp in zone AND fills<max
    """
    
    def __init__(self):
        self._fee_taker = 0.10
    
    # ── Clone Factory ────────────────────────────────────────
    
    def new_long(self) -> CloneLedger:
        return CloneLedger("LONG", "EXPANSION_UP")
    
    def new_short(self) -> CloneLedger:
        return CloneLedger("SHORT", "EXHAUSTION_DOWN")
    
    def new_grid(self) -> CloneLedger:
        return CloneLedger("GRID", "COMPRESSION_RANGE")
    
    # ── Observation ──────────────────────────────────────────
    
    def observe_long(self, ledger: CloneLedger, sp: dict, cage,
                     dir_bus, atr: float, required: float) -> dict:
        """LONG observation — 1 per candle, mandatory."""
        close = sp["close"]
        floor = cage.lower
        ceiling = cage.upper
        
        dir_ok = (sp.get("st_dir") == 1 and dir_bus.ema > 5000 and dir_bus.vd > 5000)
        
        # Corridor
        cor_in_zone = False
        if floor is not None:
            off = ENTRY_OFFSET_BASE_K * atr + ENTRY_OFFSET_MIN_ATR * atr
            cap = ENTRY_OFFSET_MAX_CAP_PCT * close
            off = min(off, cap)
            hi = floor + off
            cor_in_zone = close >= floor and close <= hi
        
        # Fee safe
        fee_safe = False
        expected_move = 0.0
        if ceiling is not None:
            expected_move = (ceiling - close) / close * 100
            fee_safe = expected_move >= required
        
        has_position = len(ledger.positions) > 0
        
        reason = None
        if not dir_ok:
            reason = "STDIR_OR_DIRBUS_MISMATCH"
        elif not cor_in_zone:
            reason = "OUT_OF_CORRIDOR"
        elif not fee_safe:
            reason = "EXPECTED_MOVE_LESS_THAN_REQUIRED"
        elif has_position:
            reason = "POSITION_ALREADY_OPEN"
        
        entry_allowed = reason is None
        setup_score = 5000 + expected_move * 400 if entry_allowed else 2500
        setup_score = max(0, min(10000, setup_score))
        
        obs = {
            "clone_id": "LONG", "bias": ledger.bias, "ts": sp["ts"],
            "entry_allowed": entry_allowed, "no_entry_reason": reason,
            "setup_score": setup_score, "confidence": setup_score,
            "expected_move": expected_move, "required_move": required,
            "fee_safe": fee_safe, "open_position": has_position,
        }
        ledger.last_obs = obs
        return obs
    
    def observe_short(self, ledger: CloneLedger, sp: dict, cage,
                      dir_bus, atr: float, required: float) -> dict:
        """SHORT observation — mirror of LONG."""
        close = sp["close"]
        floor = cage.lower
        ceiling = cage.upper
        
        dir_ok = (sp.get("st_dir") == -1 and dir_bus.ema < 5000 and dir_bus.vd < 5000)
        
        cor_in_zone = False
        if ceiling is not None:
            off = ENTRY_OFFSET_BASE_K * atr + ENTRY_OFFSET_MIN_ATR * atr
            cap = ENTRY_OFFSET_MAX_CAP_PCT * close
            off = min(off, cap)
            lo = ceiling - off
            cor_in_zone = close <= ceiling and close >= lo
        
        fee_safe = False
        expected_move = 0.0
        if floor is not None:
            expected_move = (close - floor) / close * 100
            fee_safe = expected_move >= required
        
        has_position = len(ledger.positions) > 0
        
        reason = None
        if not dir_ok:
            reason = "STDIR_OR_DIRBUS_MISMATCH"
        elif not cor_in_zone:
            reason = "OUT_OF_CORRIDOR"
        elif not fee_safe:
            reason = "EXPECTED_MOVE_LESS_THAN_REQUIRED"
        elif has_position:
            reason = "POSITION_ALREADY_OPEN"
        
        entry_allowed = reason is None
        setup_score = 5000 + expected_move * 400 if entry_allowed else 2500
        setup_score = max(0, min(10000, setup_score))
        
        obs = {
            "clone_id": "SHORT", "bias": ledger.bias, "ts": sp["ts"],
            "entry_allowed": entry_allowed, "no_entry_reason": reason,
            "setup_score": setup_score, "confidence": setup_score,
            "expected_move": expected_move, "required_move": required,
            "fee_safe": fee_safe, "open_position": has_position,
        }
        ledger.last_obs = obs
        return obs
    
    def observe_grid(self, ledger: CloneLedger, sp: dict, cage,
                     required: float) -> dict:
        """GRID observation — cage-only, buta arah."""
        close = sp["close"]
        active = (cage.status in ("VALID_COMPRESSION", "LOOSE_SIDEWAY")
                  and cage.breakout == "NONE"
                  and cage.range_atr is not None
                  and cage.upper is not None
                  and cage.lower is not None)
        
        if active and cage.upper and cage.lower and close > 0:
            width_pct = (cage.upper - cage.lower) / close * 100
            active = width_pct >= 3 * required
        
        pp = cage.pp
        fills = len(ledger.positions)
        max_fills = GRID_MAX_FILLS_PER_SIDE * 2
        
        # Entry signals
        to_open = []
        if active and fills < max_fills:
            long_fills = sum(1 for p in ledger.positions if p.side == "LONG")
            short_fills = sum(1 for p in ledger.positions if p.side == "SHORT")
            if pp < GRID_BUY_ZONE_MAX and long_fills < GRID_MAX_FILLS_PER_SIDE:
                to_open.append("LONG")
            elif pp > GRID_SELL_ZONE_MIN and short_fills < GRID_MAX_FILLS_PER_SIDE:
                to_open.append("SHORT")
        
        obs = {
            "clone_id": "GRID", "bias": ledger.bias, "ts": sp["ts"],
            "entry_allowed": False, "no_entry_reason": None if active else "CAGE_NONE",
            "setup_score": 7000 if active else 2000,
            "confidence": 7000 if active else 2000,
            "grid_active": active, "grid_fills": fills,
            "grid_to_open": to_open,
            "expected_move": 0, "required_move": required,
            "fee_safe": active, "open_position": fills > 0,
        }
        ledger.last_obs = obs
        return obs
    
    # ── Entry ────────────────────────────────────────────────
    
    def enter_long(self, ledger: CloneLedger, sp: dict, cage) -> Optional[TradeMarker]:
        close = sp["close"]
        floor = cage.lower if cage.lower else close
        ceiling = cage.upper
        atr = sp.get("atr", close * 0.01)
        
        sl = floor
        tp = close + TP_ATR_MULT * atr
        if ceiling:
            tp = min(ceiling, tp)
        
        pos = Position(side="LONG", entry_price=close, sl=sl, tp=tp)
        ledger.positions.append(pos)
        
        return TradeMarker(
            ts=sp["ts"], clone="LONG", side="LONG",
            kind="ENTRY", reason="CORRIDOR",
            entry=close
        )
    
    def enter_short(self, ledger: CloneLedger, sp: dict, cage) -> Optional[TradeMarker]:
        close = sp["close"]
        ceiling = cage.upper if cage.upper else close
        floor = cage.lower
        atr = sp.get("atr", close * 0.01)
        
        sl = ceiling
        tp = close - TP_ATR_MULT * atr
        if floor:
            tp = max(floor, tp)
        
        pos = Position(side="SHORT", entry_price=close, sl=sl, tp=tp)
        ledger.positions.append(pos)
        
        return TradeMarker(
            ts=sp["ts"], clone="SHORT", side="SHORT",
            kind="ENTRY", reason="CORRIDOR",
            entry=close
        )
    
    def enter_grid(self, ledger: CloneLedger, sp: dict, side: str) -> Optional[TradeMarker]:
        close = sp["close"]
        pos = Position(side=side, entry_price=close, sl=close, tp=close)
        ledger.positions.append(pos)
        return TradeMarker(
            ts=sp["ts"], clone="GRID", side=side,
            kind="ENTRY", reason="GRID_FILL",
            entry=close
        )
    
    # ── Position Management ──────────────────────────────────
    
    def update_position(self, pos: Position, high: float, low: float, close: float):
        """Update MAE/MFE per candle."""
        pos.hold_c += 1
        if pos.side == "LONG":
            fav = (high - pos.entry_price) / pos.entry_price * 100
            adv = (pos.entry_price - low) / pos.entry_price * 100
        else:
            fav = (pos.entry_price - low) / pos.entry_price * 100
            adv = (high - pos.entry_price) / pos.entry_price * 100
        pos.mfe = max(pos.mfe, fav)
        pos.mae = min(pos.mae, -adv)
    
    # ── Exit Decision ────────────────────────────────────────
    
    def decide_exit(self, pos: Position, sp: dict, cage, exit_bus) -> Optional[tuple]:
        """
        Exit priority chain. Returns (reason, exit_price) or None.
        Priority: WRONG_ENTRY_EARLY -> WRONG_ENTRY_GEOM -> HYPOTHESIS -> SL -> HOLD -> TP -> EXIT_BUS -> TIME
        """
        close = sp["close"]
        vel = sp.get("vel")
        side = pos.side
        
        # 1-2: Wrong entry (hold <= 2)
        if pos.hold_c <= 2:
            if vel is not None:
                if side == "LONG" and vel < -WPR_VELOCITY_DEADZONE:
                    return ("WRONG_ENTRY_EARLY", close)
                if side == "SHORT" and vel > WPR_VELOCITY_DEADZONE:
                    return ("WRONG_ENTRY_EARLY", close)
            
            adv_pct = abs(close - pos.entry_price) / pos.entry_price * 100
            if adv_pct >= WRONG_ENTRY_PCT:
                return ("WRONG_ENTRY_GEOM", close)
        
        # 3: Hypothesis invalid
        if side == "LONG" and cage.breakout == "IMMINENT_DOWN":
            return ("HYPOTHESIS_INVALID", close)
        if side == "SHORT" and cage.breakout == "IMMINENT_UP":
            return ("HYPOTHESIS_INVALID", close)
        
        # 4: SL
        if side == "LONG" and close <= pos.sl:
            return ("SL", pos.sl)
        if side == "SHORT" and close >= pos.sl:
            return ("SL", pos.sl)
        
        # 5: HOLD-veto (delays TP)
        if exit_bus.hold:
            return None
        
        # 6: TP
        if side == "LONG" and close >= pos.tp:
            return ("TP", pos.tp)
        if side == "SHORT" and close <= pos.tp:
            return ("TP", pos.tp)
        
        # 7: EXIT_BUS
        rsi = sp.get("rsi")
        wpr = sp.get("wpr")
        if side == "LONG" and ((rsi and rsi > 70) or (wpr and wpr > -20)):
            return ("EXIT_BUS", close)
        if side == "SHORT" and ((rsi and rsi < 30) or (wpr and wpr < -80)):
            return ("EXIT_BUS", close)
        
        # 8: TIME_EXIT
        profit_pct = (close - pos.entry_price) / pos.entry_price * 100 if side == "LONG" else (pos.entry_price - close) / pos.entry_price * 100
        if pos.hold_c >= TIME_EXIT_CANDLES and profit_pct < REQUIRED_MOVE:
            return ("TIME_EXIT", close)
        
        return None
    
    def decide_grid_exit(self, pos: Position, sp: dict, cage, required: float) -> Optional[tuple]:
        """GRID exit decision."""
        close = sp["close"]
        side = pos.side
        
        # Range break
        if cage.status == "NONE":
            return ("RANGE_BREAK", close)
        
        # Breakout against fill
        if side == "LONG" and cage.breakout == "IMMINENT_DOWN":
            return ("RANGE_BREAK", close)
        if side == "SHORT" and cage.breakout == "IMMINENT_UP":
            return ("RANGE_BREAK", close)
        
        # Wrong entry
        adv_pct = abs(close - pos.entry_price) / pos.entry_price * 100
        if adv_pct >= WRONG_ENTRY_PCT:
            return ("WRONG_ENTRY", close)
        
        # GRID TP
        profit_pct = (close - pos.entry_price) / pos.entry_price * 100 if side == "LONG" else (pos.entry_price - close) / pos.entry_price * 100
        if profit_pct >= required:
            return ("GRID_TP", close)
        
        return None
    
    # ── Exit Marker ──────────────────────────────────────────
    
    def make_exit(self, pos: Position, sp: dict, reason: str, exit_price: float) -> TradeMarker:
        """Buat exit marker dengan P&L after-fee."""
        side = pos.side
        entry = pos.entry_price
        
        if side == "LONG":
            gross = (exit_price - entry) / entry * 100
        else:
            gross = (entry - exit_price) / entry * 100
        
        fee = self._fee_taker
        slip = 0.05
        net = gross - fee - slip
        result = "WIN" if net > 0 else ("LOSS" if net < 0 else "BREAKEVEN")
        
        return TradeMarker(
            ts=sp["ts"], clone=pos.side if side in ("LONG", "SHORT") else "GRID",
            side=side, kind="EXIT", reason=reason,
            entry=entry, exit=exit_price,
            gross=round(gross, 4), fee=fee, slip=slip,
            net=round(net, 4), result=result,
            mae=round(pos.mae, 3), mfe=round(pos.mfe, 3),
            hold=pos.hold_c
        )
