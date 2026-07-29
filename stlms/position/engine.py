"""
=====================================================
MODULE:     position_engine.py
PURPOSE:    Position Engine — position management,
            MAE/MFE tracking, trailing stop, partial TP,
            breakeven logic.
OWNER:      PHASE-11 POSITION LAYER
INPUT:      Position dataclass (imported from clone/engine),
            candle OHLC data, ATR
OUTPUT:     Updated Position with MAE/MFE/hold_c
DEPENDENCY: stlms.core.constants, stlms.clone.engine
ARCHITECTURE:
            PositionEngine manages active positions.
            update_position: per-candle MAE/MFE tracking.
            trailing_stop: adjust SL based on TRAIL_ATR_MULT.
            partial_tp: close PARTIAL_TP_PCT of position.
            breakeven: move SL to entry_price.
=====================================================
"""

from typing import Optional
from ..core.constants import TRAIL_ATR_MULT, PARTIAL_TP_PCT
from ..clone.engine import Position


class PositionEngine:
    """
    Position Engine — manages active position state.

    Responsibilities:
        1. update_position: per-candle MAE/MFE/hold_c tracking
        2. trailing_stop: adjust SL based on ATR
        3. partial_tp: close a portion of the position
        4. breakeven: move SL to entry_price

    Architecture:
        Sits after TRADE layer. Each candle, all open positions
        are updated with new OHLC data.
    """

    def __init__(self):
        self._trail_atr_mult = TRAIL_ATR_MULT
        self._partial_tp_pct = PARTIAL_TP_PCT

    # ── Position Update ────────────────────────────────────

    def update_position(
        self, pos: Position, high: float, low: float, close: float
    ) -> Position:
        """
        Update position MAE, MFE, and hold counter per candle.

        LONG:
            fav = (high - entry) / entry * 100  (MFE)
            adv = (entry - low) / entry * 100   (MAE, stored negative)

        SHORT:
            fav = (entry - low) / entry * 100   (MFE)
            adv = (high - entry) / entry * 100  (MAE, stored negative)

        Args:
            pos: Position to update
            high: candle high
            low: candle low
            close: candle close (for future use)

        Returns:
            Updated Position
        """
        pos.hold_c += 1

        if pos.side == "LONG":
            fav = (high - pos.entry_price) / pos.entry_price * 100
            adv = (pos.entry_price - low) / pos.entry_price * 100
        else:
            fav = (pos.entry_price - low) / pos.entry_price * 100
            adv = (high - pos.entry_price) / pos.entry_price * 100

        pos.mfe = max(pos.mfe, fav)
        pos.mae = min(pos.mae, -adv)

        return pos

    # ── Trailing Stop ──────────────────────────────────────

    def trailing_stop(self, pos: Position, atr: float) -> Optional[float]:
        """
        Calculate new trailing stop level based on ATR.

        For LONG:
            new_sl = close - TRAIL_ATR_MULT * atr
            Only move SL upward (tightening), never downward.

        For SHORT:
            new_sl = close + TRAIL_ATR_MULT * atr
            Only move SL downward (tightening), never upward.

        Args:
            pos: current position
            atr: current ATR value

        Returns:
            New SL price if tighter than current SL, else None.
        """
        trail_distance = self._trail_atr_mult * atr

        if pos.side == "LONG":
            new_sl = pos.entry_price - trail_distance
            if new_sl > pos.sl:
                pos.sl = new_sl
                return new_sl
        else:
            new_sl = pos.entry_price + trail_distance
            if new_sl < pos.sl:
                pos.sl = new_sl
                return new_sl

        return None

    # ── Partial TP ─────────────────────────────────────────

    def partial_tp(self, pos: Position, close: float) -> bool:
        """
        Close a portion of the position at take-profit.

        PARTIAL_TP_PCT (default 0.5 = 50%) of position is closed.
        Remaining position SL is moved to breakeven.

        Args:
            pos: current position
            close: current close price

        Returns:
            True if partial TP was triggered, False otherwise.
        """
        if pos.side == "LONG":
            tp_triggered = close >= pos.tp
        else:
            tp_triggered = close <= pos.tp

        if tp_triggered:
            pos.status = "PARTIAL"
            return True

        return False

    # ── Breakeven ──────────────────────────────────────────

    def breakeven(self, pos: Position) -> Optional[float]:
        """
        Move stop-loss to entry price (breakeven).

        Typically called after partial TP or when trailing
        stop reaches entry level.

        Args:
            pos: current position

        Returns:
            New SL (entry_price) if changed, else None.
        """
        if abs(pos.sl - pos.entry_price) > 1e-8:
            old_sl = pos.sl
            pos.sl = pos.entry_price
            pos.status = "BREAKEVEN"
            return pos.sl
        return None

    # ── Position State Helpers ─────────────────────────────

    def is_open(self, pos: Position) -> bool:
        """Check if position is still open."""
        return pos.status in ("OPEN", "HOLD", "TRAILING", "BREAKEVEN", "PARTIAL")

    def unrealized_pnl(self, pos: Position, close: float) -> float:
        """Calculate unrealized P&L at current price."""
        if pos.side == "LONG":
            return (close - pos.entry_price) / pos.entry_price * 100
        else:
            return (pos.entry_price - close) / pos.entry_price * 100
