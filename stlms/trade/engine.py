"""
=====================================================
MODULE:     trade_engine.py
PURPOSE:    Trade Engine — ENTRY/EXIT marker production,
            fee calculation, P&L, adverse-first logic.
OWNER:      PHASE-10 TRADE LAYER
INPUT:      Clone observations, candle data, Position
OUTPUT:     TradeMarker dataclass (imported from clone/engine)
DEPENDENCY: stlms.core.constants, stlms.clone.engine
ARCHITECTURE:
            TradeEngine adalah lapisan antara CLONE dan POSITION.
            CloneEngine menentukan kapan entry/exit; TradeEngine
            membuat marker dengan fee, slip, dan P&L calculation.
            Adverse-first: jika SL dan TP terjadi di candle yang sama,
            SL diprioritaskan (worst-case principle).
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional
from ..core.constants import (
    FEE_MAKER, FEE_TAKER, SLIP_ESTIMATE
)
from ..clone.engine import TradeMarker, Position


class TradeEngine:
    """
    Trade Engine — produces TradeMarker for ENTRY and EXIT.

    Responsibilities:
        1. make_entry: create ENTRY marker with entry price, SL, TP
        2. make_exit: create EXIT marker with full P&L calculation
        3. Fee calculation: maker 0.04%, taker 0.10%, slip 0.05%
        4. P&L: gross = (exit-entry)/entry*100 (LONG), net = gross - fee - slip
        5. Adverse-first: SL beats TP on same candle

    Architecture:
        Sits between CLONE and POSITION layers.
        CloneEngine triggers entry/exit; TradeEngine formalizes markers.
    """

    def __init__(self):
        self._fee_maker = FEE_MAKER
        self._fee_taker = FEE_TAKER
        self._slip = SLIP_ESTIMATE

    # ── Entry Marker ────────────────────────────────────────

    def make_entry(
        self, ts: int, clone: str, side: str,
        entry_price: float, sl: float, tp: float
    ) -> TradeMarker:
        """
        Create an ENTRY TradeMarker.

        Args:
            ts: timestamp in ms
            clone: clone ID (LONG / SHORT / GRID)
            side: trade side (LONG / SHORT)
            entry_price: entry fill price
            sl: stop-loss price
            tp: take-profit price

        Returns:
            TradeMarker with kind=ENTRY, P&L fields set to None
        """
        return TradeMarker(
            ts=ts, clone=clone, side=side,
            kind="ENTRY", reason="CORRIDOR",
            entry=entry_price
        )

    # ── Exit Marker ─────────────────────────────────────────

    def make_exit(
        self, ts: int, clone: str, side: str,
        reason: str, entry_price: float,
        exit_price: float, position: Optional[Position] = None
    ) -> TradeMarker:
        """
        Create an EXIT TradeMarker with full P&L calculation.

        P&L formula:
            LONG:  gross = (exit - entry) / entry * 100
            SHORT: gross = (entry - exit) / entry * 100
            net = gross - fee - slip
            result = WIN if net > 0 else LOSS

        Fee: taker 0.10% (entry+exit)
        Slip: 0.05% constant

        Args:
            ts: timestamp in ms
            clone: clone ID
            side: trade side (LONG / SHORT)
            reason: exit reason string
            entry_price: original entry price
            exit_price: exit fill price
            position: optional Position for MAE/MFE/hold carry-over

        Returns:
            TradeMarker with kind=EXIT, full P&L populated
        """
        if side == "LONG":
            gross = (exit_price - entry_price) / entry_price * 100
        else:
            gross = (entry_price - exit_price) / entry_price * 100

        fee = self._fee_taker
        slip = self._slip
        net = gross - fee - slip
        result = "WIN" if net > 0 else ("LOSS" if net < 0 else "BREAKEVEN")

        mae = round(position.mae, 3) if position else 0.0
        mfe = round(position.mfe, 3) if position else 0.0
        hold = position.hold_c if position else 0

        return TradeMarker(
            ts=ts, clone=clone, side=side,
            kind="EXIT", reason=reason,
            entry=entry_price, exit=exit_price,
            gross=round(gross, 4), fee=fee, slip=slip,
            net=round(net, 4), result=result,
            mae=mae, mfe=mfe, hold=hold
        )

    # ── P&L Calculation ─────────────────────────────────────

    def calc_pnl(self, side: str, entry_price: float,
                 exit_price: float) -> dict:
        """
        Standalone P&L calculation without creating a marker.

        Returns:
            dict with gross, fee, slip, net, result
        """
        if side == "LONG":
            gross = (exit_price - entry_price) / entry_price * 100
        else:
            gross = (entry_price - exit_price) / entry_price * 100

        fee = self._fee_taker
        slip = self._slip
        net = gross - fee - slip
        result = "WIN" if net > 0 else ("LOSS" if net < 0 else "BREAKEVEN")

        return {
            "gross": round(gross, 4),
            "fee": fee,
            "slip": slip,
            "net": round(net, 4),
            "result": result,
        }

    # ── Adverse-First ───────────────────────────────────────

    def resolve_adverse_first(
        self, sl_hit: bool, tp_hit: bool
    ) -> tuple[bool, bool]:
        """
        Adverse-first principle: if both SL and TP trigger
        on the same candle, SL takes priority.

        Returns:
            (effective_sl_hit, effective_tp_hit)
        """
        if sl_hit and tp_hit:
            return (True, False)
        return (sl_hit, tp_hit)

    # ── Fee Helpers ─────────────────────────────────────────

    def get_fee(self, is_maker: bool = False) -> float:
        """Return applicable fee rate."""
        return self._fee_maker if is_maker else self._fee_taker

    def get_slip(self) -> float:
        """Return slip estimate."""
        return self._slip
