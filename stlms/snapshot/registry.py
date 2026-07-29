"""
ST-LMS v3 — Snapshot Registry
Snapshot System — Phase 1

Registers 10 snapshot types with W/OD field classification.
W fields are frozen-stored; OD fields are computed deterministically.
Reference: LAW-MASTER-16 (Snapshot), IMPLEMENTATION_FREEZE.md
"""

from typing import Any

SNAPSHOT_TYPE_DEFINITIONS = {
    "market_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "open", "high", "low", "close",
            "volume", "taker_buy_ratio", "data_status", "gap_flag",
        ],
        "OD": [
            "wib_iso", "typical_price", "median_price", "weighted_price",
            "log_return", "range_pct", "body_pct", "upper_wick_pct",
            "lower_wick_pct",
        ],
    },
    "truth_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "open", "high", "low", "close",
            "volume", "data_status",
        ],
        "OD": [
            "wib_iso", "truth_range", "atr_normalized", "volatility_ratio",
            "gap_risk",
        ],
    },
    "structure_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "support_levels", "resistance_levels",
            "trend_strength", "wave_structure", "cage_status", "cage_breakout",
            "market_phase",
        ],
        "OD": [
            "wib_iso", "swing_ratio", "structure_score", "compression_score",
            "breakout_probability",
        ],
    },
    "evidence_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "long_signals", "short_signals",
            "consensus_level", "conflict_level", "bag_weights",
        ],
        "OD": [
            "wib_iso", "evidence_strength", "conviction_score",
            "divergence_flag", "alignment_score",
        ],
    },
    "clone_observation": {
        "W": [
            "ts", "symbol", "timeframe", "clone_kind", "entry_price",
            "stop_loss", "take_profit", "position_size", "risk_reward",
            "confidence",
        ],
        "OD": [
            "wib_iso", "expected_value", "risk_pct", "optimal_f",
            "position_score",
        ],
    },
    "trade_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "trade_kind", "trade_side",
            "entry_price", "exit_price", "quantity", "pnl", "pnl_pct",
            "trade_result",
        ],
        "OD": [
            "wib_iso", "cumulative_pnl", "win_streak", "loss_streak",
            "sharpe_estimate",
        ],
    },
    "position_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "position_status", "entry_price",
            "current_price", "quantity", "unrealized_pnl", "unrealized_pnl_pct",
            "stop_loss", "take_profit",
        ],
        "OD": [
            "wib_iso", "position_heat", "distance_to_stop_pct",
            "distance_to_target_pct", "risk_exposure",
        ],
    },
    "statistics_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "total_trades", "win_count",
            "loss_count", "win_rate", "avg_win", "avg_loss", "profit_factor",
            "max_drawdown_pct",
        ],
        "OD": [
            "wib_iso", "expectancy", "sharpe_ratio", "sortino_ratio",
            "calmar_ratio", "recovery_factor",
        ],
    },
    "knowledge_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "knowledge_entity", "librarian_status",
            "pattern_signature", "success_rate", "sample_count",
        ],
        "OD": [
            "wib_iso", "confidence_interval", "maturity_score",
            "reliability_index", "decay_factor",
        ],
    },
    "prediction_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "prediction_source", "direction",
            "probability", "target_price", "horizon_seconds",
        ],
        "OD": [
            "wib_iso", "certainty_score", "prediction_range_low",
            "prediction_range_high", "time_decay_factor",
        ],
    },
    "benchmark_snapshot": {
        "W": [
            "ts", "symbol", "timeframe", "benchmark_kind", "total_return_pct",
            "annualized_return_pct", "max_drawdown_pct", "sharpe_ratio",
            "win_rate", "profit_factor",
        ],
        "OD": [
            "wib_iso", "sortino_ratio", "calmar_ratio", "omega_ratio",
            "var_95", "cvar_95",
        ],
    },
}


class SnapshotRegistry:
    """Registry for snapshot type definitions with W/OD field classification."""

    def __init__(self):
        self._types: dict[str, dict] = dict(SNAPSHOT_TYPE_DEFINITIONS)

    def validate_snapshot(self, snapshot_type: str, fields: dict) -> bool:
        if snapshot_type not in self._types:
            raise ValueError(f"Unknown snapshot type: {snapshot_type}")
        definition = self._types[snapshot_type]
        w_fields = set(definition["W"])
        for wf in w_fields:
            if wf not in fields:
                raise ValueError(f"Missing W field '{wf}' in {snapshot_type}")
            if fields[wf] is None:
                raise ValueError(f"W field '{wf}' is null in {snapshot_type}")
        od_fields = set(definition["OD"])
        for odf in od_fields:
            if odf in fields:
                raise ValueError(
                    f"OD field '{odf}' must not be in stored payload for {snapshot_type}"
                )
        return True

    def list_types(self) -> list[str]:
        return sorted(self._types.keys())

    def get_fields(self, snapshot_type: str) -> dict[str, list[str]]:
        if snapshot_type not in self._types:
            raise ValueError(f"Unknown snapshot type: {snapshot_type}")
        definition = self._types[snapshot_type]
        return {
            "W": list(definition["W"]),
            "OD": list(definition["OD"]),
        }

    def get_w_fields(self, snapshot_type: str) -> list[str]:
        return self.get_fields(snapshot_type)["W"]

    def get_od_fields(self, snapshot_type: str) -> list[str]:
        return self.get_fields(snapshot_type)["OD"]

    def type_count(self) -> int:
        return len(self._types)

    def summary(self) -> dict:
        return {
            "total_types": self.type_count(),
            "types": self.list_types(),
            "fields_per_type": {
                t: {
                    "W": len(self._types[t]["W"]),
                    "OD": len(self._types[t]["OD"]),
                }
                for t in self.list_types()
            },
        }
