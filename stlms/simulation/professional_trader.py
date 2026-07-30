"""
Professional Futures Trader Simulation — PHASE-12.
Simulates how a professional futures trader would trade.
Entry, Position sizing, Scaling, Margin, Leverage, Risk, TP, SL,
Breakeven, Profit lock, Trailing, Capital allocation, Clone competition.
STATUS: EVOLUTION_ALLOWED
"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TradeDecision:
    action: str  # ENTRY, EXIT, HOLD, SCALE_UP, SCALE_DOWN, PARTIAL_TP, BREAKEVEN, TRAILING
    side: str    # LONG, SHORT
    size_pct: float  # percentage of capital
    entry_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    leverage: int = 5
    reason: str = ""
    confidence: float = 0.0

@dataclass
class PositionIntelligence:
    total_positions: int = 0
    winning_pct: float = 0.0
    avg_profit_pct: float = 0.0
    best_line_type: str = ""
    best_wave_type: str = ""
    worst_pattern: str = ""
    profit_by_line_type: dict = field(default_factory=dict)
    loss_by_pattern: dict = field(default_factory=dict)

class ProfessionalTraderSimulator:
    def __init__(self, capital=100.0, leverage=5, risk_per_trade=0.02):
        self._capital = capital
        self._leverage = leverage
        self._risk_per_trade = risk_per_trade
        self._positions: list = []
        self._trade_history: list = []
        self._position_intel = PositionIntelligence()
    
    def evaluate_entry(self, truth, structure, knowledge, prediction) -> TradeDecision:
        """Evaluate whether to enter a trade based on all available data."""
        bias = prediction.get("dominant_bias", "NEUTRAL")
        score = prediction.get("intelligence_score", 5000)
        
        if bias == "NEUTRAL" or score < 6000:
            return TradeDecision(action="HOLD", side="NONE", size_pct=0, reason="Insufficient confidence")
        
        atr = truth.get("atr", 100) if isinstance(truth, dict) else getattr(truth, 'atr', 100)
        entry_price = truth.get("close", 0) if isinstance(truth, dict) else getattr(truth, 'close', 0)
        
        stop_distance = atr * 1.5
        if bias == "BULLISH":
            sl = entry_price - stop_distance
            tp = entry_price + stop_distance * 2
            return TradeDecision(action="ENTRY", side="LONG", size_pct=0.3,
                               entry_price=entry_price, stop_loss=sl, take_profit=tp,
                               leverage=self._leverage, reason=f"BULLISH bias, score={score}")
        else:
            sl = entry_price + stop_distance
            tp = entry_price - stop_distance * 2
            return TradeDecision(action="ENTRY", side="SHORT", size_pct=0.3,
                               entry_price=entry_price, stop_loss=sl, take_profit=tp,
                               leverage=self._leverage, reason=f"BEARISH bias, score={score}")
    
    def calculate_position_size(self, capital, entry_price, stop_loss, risk_pct=None):
        """Calculate position size based on risk management."""
        risk = risk_pct or self._risk_per_trade
        risk_amount = capital * risk
        stop_distance = abs(entry_price - stop_loss)
        if stop_distance == 0:
            return 0
        position_size = risk_amount / stop_distance
        return min(position_size, capital * 0.5 / entry_price)
    
    def calculate_margin(self, position_size, leverage=None):
        lev = leverage or self._leverage
        return position_size / lev
    
    def calculate_liquidation_price(self, entry_price, leverage, side):
        if side == "LONG":
            return entry_price * (1 - 1.0 / leverage * 0.8)
        else:
            return entry_price * (1 + 1.0 / leverage * 0.8)
    
    def manage_scaling(self, current_position, market_character, confidence):
        """Scale into position based on market character and confidence."""
        if market_character in ("STRONG_BULL", "STRONG_BEAR") and confidence > 0.8:
            return TradeDecision(action="SCALE_UP", side=current_position.get("side", "LONG"),
                               size_pct=0.2, reason=f"Strong trend + high confidence ({confidence:.0%})")
        if market_character in ("REVERSAL", "EXHAUSTION") and confidence < 0.5:
            return TradeDecision(action="SCALE_DOWN", side=current_position.get("side", "LONG"),
                               size_pct=0.5, reason="Weak signal — reducing exposure")
        return TradeDecision(action="HOLD", side=current_position.get("side", "LONG"),
                           size_pct=0, reason="No scaling signal")
    
    def manage_partial_tp(self, position, profit_pct, market_state):
        """Take partial profit at milestones."""
        if profit_pct >= 0.05 and market_state == "STRONG_BULL":
            return {"action": "PARTIAL_TP", "close_pct": 0.25, "reason": "5% profit, strong trend"}
        if profit_pct >= 0.10:
            return {"action": "PARTIAL_TP", "close_pct": 0.50, "reason": "10% profit"}
        if profit_pct >= 0.20:
            return {"action": "PARTIAL_TP", "close_pct": 0.75, "reason": "20% profit"}
        return {"action": "HOLD", "close_pct": 0}
    
    def manage_trailing_stop(self, position, current_price, atr):
        """Update trailing stop based on ATR."""
        side = position.get("side", "LONG")
        if side == "LONG":
            new_sl = current_price - atr * 2
            return max(new_sl, position.get("stop_loss", 0))
        else:
            new_sl = current_price + atr * 2
            return min(new_sl, position.get("stop_loss", float("inf")))
    
    def manage_breakeven(self, position, current_price):
        """Move stop loss to breakeven when in profit."""
        entry = position.get("entry_price", 0)
        sl = position.get("stop_loss", 0)
        side = position.get("side", "LONG")
        if side == "LONG" and current_price > entry * 1.01:
            return True
        if side == "SHORT" and current_price < entry * 0.99:
            return True
        return False
    
    def manage_profit_lock(self, position, profit_pct):
        """Lock in profit when reaching significant gains."""
        if profit_pct >= 0.15:
            return True
        return False
    
    def evaluate_emergency_exit(self, position, market_character, liquidation_risk):
        """Emergency exit conditions."""
        if liquidation_risk > 0.8:
            return True
        if market_character in ("CHAOTIC", "FAKE_BREAKOUT"):
            return True
        return False
    
    def run_clone_competition(self, clones_data):
        """Compare clone performance."""
        scores = {}
        for clone_id, data in clones_data.items():
            win_rate = data.get("win_rate", 0)
            expectancy = data.get("expectancy", 0)
            sample = data.get("sample", 0)
            if sample > 0:
                scores[clone_id] = win_rate * 0.6 + max(0, expectancy / 100) * 0.4
        return scores
    
    def get_clone_scores(self, statistics):
        scores = {}
        for clone_id, stats in statistics.items():
            if isinstance(stats, dict) and stats.get("sample", 0) > 0:
                scores[clone_id] = {
                    "win_rate": stats.get("win_rate", 0),
                    "expectancy": stats.get("expectancy", 0),
                    "sample": stats.get("sample", 0),
                    "score": stats.get("win_rate", 0) * 0.6 + max(0, stats.get("expectancy", 0) / 100) * 0.4,
                }
        return scores
    
    def get_position_intelligence(self):
        return self._position_intel
    
    def simulate_trade(self, entry_decision, market_data):
        """Simulate a single trade from entry to exit."""
        self._trade_history.append({
            "decision": entry_decision,
            "market_snapshot": str(market_data)[:100] if market_data else "N/A",
        })
        return {"status": "SIMULATED", "action": entry_decision.action}
