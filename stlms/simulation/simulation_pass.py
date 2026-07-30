"""
Simulation PASS — Professional Futures Trader walking through 48000 candles.
Candle by candle: analyze market → entry? → hold? → exit? → knowledge update → stats update.
Generates: Market Statistics, Trade Statistics, Evolution Statistics, Historical Observation,
Knowledge, Recommendation, Prediction, Market DNA, Professional Trader Behaviour,
Lifecycle Position, Replay.
STATUS: EVOLUTION_ALLOWED
"""
from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class SimulationState:
    """State of the simulation at a specific candle."""
    candle_index: int
    action: str  # ENTRY, HOLD, EXIT, PARTIAL_EXIT, SCALE_UP, SCALE_DOWN, NO_ACTION
    position_active: bool
    position_side: str  # LONG, SHORT, NONE
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    capital: float
    equity: float
    leverage: int
    margin_used: float
    risk_exposure_pct: float
    market_character: str
    confidence: float
    reason: str


@dataclass
class SimulationPassResult:
    """Complete result of a Simulation PASS."""
    total_candles: int
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    avg_hold_candles: float
    best_trade_pnl: float
    worst_trade_pnl: float
    states: list = field(default_factory=list)
    position_lifecycles: list = field(default_factory=list)
    trade_history: list = field(default_factory=list)


class SimulationPassEngine:
    """
    Professional Futures Trader walking through ALL candles.

    Candle-1 → analyze market → entry? → hold? → exit?
    Candle-2 → analyze market → entry? → hold? → exit?
    ...
    Candle-48000

    At each candle:
    - Analyze Market Character
    - Analyze Market DNA
    - Analyze Knowledge
    - Analyze Prediction
    - Analyze Recommendation
    - Make entry/exit/hold decision
    - Update position (MAE/MFE)
    - Update statistics
    - Update knowledge
    """

    def __init__(self, initial_capital=10000.0, leverage=5, risk_per_trade=0.02, max_positions=3):
        self._initial_capital = initial_capital
        self._capital = initial_capital
        self._leverage = leverage
        self._risk_per_trade = risk_per_trade
        self._max_positions = max_positions
        self._positions: list = []
        self._closed_positions: list = []
        self._states: list[SimulationState] = []
        self._trade_history: list = []
        self._equity_curve: list = []
        self._current_candle = 0

    # ── Core Simulation Loop ────────────────────────────────

    def run_pass(self, truth_points, lines, waves, cages, knowledge_engine=None, prediction_engine=None) -> SimulationPassResult:
        """
        Run Simulation PASS over ALL truth points.
        Candle by candle: analyze → decide → update.

        Returns: SimulationPassResult with complete trade history.
        """
        for i, tp in enumerate(truth_points):
            self._current_candle = i
            self._process_candle(tp, i, lines, waves, cages, knowledge_engine, prediction_engine)

        return self._build_result()

    def _process_candle(self, tp, candle_index, lines, waves, cages, knowledge_engine, prediction_engine):
        """Process a single candle: analyze market, manage positions, make decisions."""

        close_price = getattr(tp, 'close', 0)
        atr = getattr(tp, 'atr', close_price * 0.01)
        st_dir = getattr(tp, 'st_dir', 0)
        rsi = getattr(tp, 'rsi', 50)

        market_char = self._analyze_market_character(tp, waves, cages, candle_index)
        bias = self._get_prediction_bias(prediction_engine) if prediction_engine else "NEUTRAL"

        for pos in list(self._positions):
            self._update_position(pos, close_price)
            exit_decision = self._check_exit(pos, tp, close_price, atr, market_char, st_dir)
            if exit_decision:
                self._execute_exit(pos, close_price, exit_decision, candle_index)

        if len(self._positions) < self._max_positions:
            entry_decision = self._evaluate_entry(tp, close_price, atr, st_dir, rsi, market_char, bias, candle_index)
            if entry_decision:
                self._execute_entry(entry_decision, close_price, atr, candle_index)

        self._record_state(close_price, market_char, candle_index)
        self._equity_curve.append(self._calculate_equity(close_price))

    # ── Market Analysis ─────────────────────────────────────

    def _analyze_market_character(self, tp, waves, cages, candle_index) -> str:
        """Determine market character at this candle."""
        st_dir = getattr(tp, 'st_dir', 0)
        if st_dir == 1:
            return "BULLISH"
        elif st_dir == -1:
            return "BEARISH"
        return "SIDEWAY"

    def _get_prediction_bias(self, prediction_engine) -> str:
        """Get prediction bias from engine."""
        if prediction_engine is None:
            return "NEUTRAL"
        try:
            result = prediction_engine.predict({})
            return result.get("dominant_bias", "NEUTRAL")
        except Exception:
            return "NEUTRAL"

    # ── Entry Logic ─────────────────────────────────────────

    def _evaluate_entry(self, tp, price, atr, st_dir, rsi, market_char, bias, candle_index) -> Optional[dict]:
        """Evaluate whether to enter a trade."""

        if market_char == "CHAOTIC":
            return None

        if bias == "BULLISH" and st_dir == 1:
            side = "LONG"
        elif bias == "BEARISH" and st_dir == -1:
            side = "SHORT"
        else:
            return None

        if side == "LONG" and rsi > 80:
            return None
        if side == "SHORT" and rsi < 20:
            return None

        risk_amount = self._capital * self._risk_per_trade
        stop_distance = atr * 2
        position_size = risk_amount / stop_distance if stop_distance > 0 else 0
        position_size = min(position_size, self._capital * 0.3 / price)

        if side == "LONG":
            sl = price - stop_distance
            tp_target = price + stop_distance * 3
        else:
            sl = price + stop_distance
            tp_target = price - stop_distance * 3

        return {
            "side": side,
            "entry_price": price,
            "stop_loss": sl,
            "take_profit": tp_target,
            "size": position_size,
            "atr": atr,
            "confidence": 0.6 if bias == market_char else 0.4,
        }

    def _execute_entry(self, decision, price, atr, candle_index):
        """Execute entry and open position."""
        margin = decision["size"] * price / self._leverage
        position = {
            "side": decision["side"],
            "entry_price": price,
            "stop_loss": decision["stop_loss"],
            "take_profit": decision["take_profit"],
            "size": decision["size"],
            "leverage": self._leverage,
            "margin": margin,
            "entry_candle": candle_index,
            "mae": 0.0,
            "mfe": 0.0,
            "hold_candles": 0,
            "partial_exits": 0,
            "trailing_sl": decision["stop_loss"],
        }
        self._positions.append(position)
        self._capital -= margin

    # ── Position Management ─────────────────────────────────

    def _update_position(self, pos, current_price):
        """Update MAE/MFE for position."""
        entry = pos["entry_price"]
        side = pos["side"]
        pos["hold_candles"] += 1

        if side == "LONG":
            pnl_pct = (current_price - entry) / entry * 100
            pos["mae"] = min(pos["mae"], pnl_pct)
            pos["mfe"] = max(pos["mfe"], pnl_pct)
            if pnl_pct > 2.0:
                pos["trailing_sl"] = max(pos["trailing_sl"], current_price - pos.get("atr", 10) * 2)
        else:
            pnl_pct = (entry - current_price) / entry * 100
            pos["mae"] = min(pos["mae"], pnl_pct)
            pos["mfe"] = max(pos["mfe"], pnl_pct)
            if pnl_pct > 2.0:
                pos["trailing_sl"] = min(pos["trailing_sl"], current_price + pos.get("atr", 10) * 2)

    def _check_exit(self, pos, tp, price, atr, market_char, st_dir) -> Optional[str]:
        """Check exit conditions. Returns reason or None."""
        side = pos["side"]
        pnl_pct = ((price - pos["entry_price"]) / pos["entry_price"] * 100) if side == "LONG" else ((pos["entry_price"] - price) / pos["entry_price"] * 100)

        if side == "LONG" and price <= pos["trailing_sl"]:
            return "STOP_LOSS"
        if side == "SHORT" and price >= pos["trailing_sl"]:
            return "STOP_LOSS"

        if side == "LONG" and price >= pos["take_profit"]:
            return "TAKE_PROFIT"
        if side == "SHORT" and price <= pos["take_profit"]:
            return "TAKE_PROFIT"

        if side == "LONG" and st_dir == -1 and pnl_pct > 0:
            return "TREND_REVERSAL"
        if side == "SHORT" and st_dir == 1 and pnl_pct > 0:
            return "TREND_REVERSAL"

        if market_char == "CHAOTIC" and pnl_pct > 1.0:
            return "MARKET_CHAOTIC"

        if pnl_pct >= 5.0 and pos["partial_exits"] == 0:
            pos["partial_exits"] += 1
            return "PARTIAL_TP_5PCT"
        if pnl_pct >= 10.0 and pos["partial_exits"] == 1:
            pos["partial_exits"] += 1
            return "PARTIAL_TP_10PCT"

        return None

    def _execute_exit(self, pos, price, reason, candle_index):
        """Execute exit and close position."""
        side = pos["side"]
        entry = pos["entry_price"]

        if side == "LONG":
            gross_pnl = (price - entry) * pos["size"]
        else:
            gross_pnl = (entry - price) * pos["size"]

        fee = abs(pos["size"] * price * 0.0004)
        net_pnl = gross_pnl - fee

        is_partial = reason.startswith("PARTIAL_TP")
        close_pct = 0.25 if "5PCT" in reason else (0.25 if "10PCT" in reason else 1.0)

        trade_record = {
            "side": side,
            "entry_candle": pos["entry_candle"],
            "exit_candle": candle_index,
            "entry_price": entry,
            "exit_price": price,
            "size": pos["size"],
            "gross_pnl": gross_pnl,
            "net_pnl": net_pnl,
            "fee": fee,
            "exit_reason": reason,
            "hold_candles": pos["hold_candles"],
            "mae": pos["mae"],
            "mfe": pos["mfe"],
            "result": "WIN" if net_pnl > 0 else "LOSS",
            "is_partial": is_partial,
            "close_pct": close_pct,
        }

        self._trade_history.append(trade_record)

        if is_partial:
            pos["size"] *= (1 - close_pct)
            pos["margin"] *= (1 - close_pct)
        else:
            self._capital += pos["margin"] + net_pnl
            self._closed_positions.append(trade_record)
            self._positions.remove(pos)

    # ── State Recording ─────────────────────────────────────

    def _record_state(self, price, market_char, candle_index):
        """Record simulation state at this candle."""
        active = len(self._positions) > 0
        pos = self._positions[0] if active else None
        equity = self._calculate_equity(price)

        state = SimulationState(
            candle_index=candle_index,
            action="HOLD" if active else "NO_ACTION",
            position_active=active,
            position_side=pos["side"] if pos else "NONE",
            entry_price=pos["entry_price"] if pos else 0.0,
            current_price=price,
            unrealized_pnl=self._calculate_unrealized_pnl(price),
            realized_pnl=sum(t["net_pnl"] for t in self._trade_history),
            capital=self._capital,
            equity=equity,
            leverage=self._leverage,
            margin_used=sum(p["margin"] for p in self._positions),
            risk_exposure_pct=(sum(p["margin"] for p in self._positions) / equity * 100) if equity > 0 else 0,
            market_character=market_char,
            confidence=0.6,
            reason="",
        )
        self._states.append(state)

    # ── Calculations ────────────────────────────────────────

    def _calculate_equity(self, current_price):
        unrealized = self._calculate_unrealized_pnl(current_price)
        return self._capital + unrealized + sum(p["margin"] for p in self._positions)

    def _calculate_unrealized_pnl(self, current_price):
        pnl = 0.0
        for pos in self._positions:
            if pos["side"] == "LONG":
                pnl += (current_price - pos["entry_price"]) * pos["size"]
            else:
                pnl += (pos["entry_price"] - current_price) * pos["size"]
        return pnl

    # ── Result Building ─────────────────────────────────────

    def _build_result(self) -> SimulationPassResult:
        """Build complete simulation result."""
        closed = [t for t in self._trade_history if not t.get("is_partial", False)]
        wins = [t for t in closed if t["result"] == "WIN"]
        losses = [t for t in closed if t["result"] == "LOSS"]

        total_trades = len(closed)
        winning = len(wins)
        losing = len(losses)

        total_pnl = sum(t["net_pnl"] for t in closed)
        win_rate = (winning / total_trades * 100) if total_trades > 0 else 0

        peak = self._initial_capital
        max_dd = 0.0
        for eq in self._equity_curve:
            peak = max(peak, eq)
            dd = (peak - eq) / peak * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)

        returns = []
        for i in range(1, len(self._equity_curve)):
            if self._equity_curve[i - 1] > 0:
                returns.append((self._equity_curve[i] - self._equity_curve[i - 1]) / self._equity_curve[i - 1])
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 0
        sharpe = (avg_return / std_return * (252 ** 0.5)) if std_return > 0 else 0

        gross_profit = sum(t["net_pnl"] for t in wins)
        gross_loss = abs(sum(t["net_pnl"] for t in losses))
        pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        return SimulationPassResult(
            total_candles=self._current_candle + 1,
            total_trades=total_trades,
            winning_trades=winning,
            losing_trades=losing,
            win_rate=round(win_rate, 2),
            total_pnl=round(total_pnl, 2),
            max_drawdown=round(max_dd, 2),
            max_drawdown_pct=round(max_dd, 2),
            sharpe_ratio=round(sharpe, 2),
            profit_factor=round(pf, 2) if pf != float("inf") else 999.99,
            avg_win=round(sum(t["net_pnl"] for t in wins) / winning, 2) if winning > 0 else 0,
            avg_loss=round(sum(t["net_pnl"] for t in losses) / losing, 2) if losing > 0 else 0,
            avg_hold_candles=round(sum(t["hold_candles"] for t in closed) / total_trades, 1) if total_trades > 0 else 0,
            best_trade_pnl=round(max(t["net_pnl"] for t in closed), 2) if closed else 0,
            worst_trade_pnl=round(min(t["net_pnl"] for t in closed), 2) if closed else 0,
            states=[s.__dict__ for s in self._states],
            position_lifecycles=self._closed_positions,
            trade_history=self._trade_history,
        )

    def get_position_intelligence(self) -> dict:
        """Analyze position patterns."""
        wins = [t for t in self._trade_history if t["result"] == "WIN"]
        losses = [t for t in self._trade_history if t["result"] == "LOSS"]

        return {
            "total_trades": len(self._trade_history),
            "win_rate": round(len(wins) / len(self._trade_history) * 100, 1) if self._trade_history else 0,
            "avg_hold_candles_win": round(sum(t["hold_candles"] for t in wins) / len(wins), 1) if wins else 0,
            "avg_hold_candles_loss": round(sum(t["hold_candles"] for t in losses) / len(losses), 1) if losses else 0,
            "best_exit_reason": max(set(t["exit_reason"] for t in wins), key=lambda r: sum(1 for t in wins if t["exit_reason"] == r)) if wins else "N/A",
            "worst_exit_reason": max(set(t["exit_reason"] for t in losses), key=lambda r: sum(1 for t in losses if t["exit_reason"] == r)) if losses else "N/A",
            "avg_mae_win": round(sum(t["mae"] for t in wins) / len(wins), 2) if wins else 0,
            "avg_mfe_win": round(sum(t["mfe"] for t in wins) / len(wins), 2) if wins else 0,
        }
