# SIMULATION LAYER OUTPUT CONTRACT

## ST-LMS v3 — Phase 0.5 Implementation Enrichment

**Date:** 2026-07-29
**Status:** CONTRACT DEFINITION — FROZEN
**Phase:** PHASE-16 (Simulation Layer)

---

## SIMULATION LAYER OVERVIEW

Simulation Layer memiliki 5 simulator. Setiap simulator memiliki Input Contract, Output Contract, Generated Artifact, Consumer, Success Criteria, dan Failure Criteria.

---

## 1. ARCHITECTURE SIMULATOR

### Purpose
Memvalidasi seluruh pipeline ST-LMS — memastikan 23 stages berjalan benar, card sharing valid, determinisme terverifikasi, unidirectional flow terjaga, dan tidak ada circular dependency.

### Input Contract
```json
{
  "architecture_simulation_input": {
    "pipeline_config": {
      "stages": 23,
      "shared_stages": [1, 2, 3, 4],
      "per_clone_stages": [5, 6, 7, 8, 9, 10, 11],
      "shared_again_stages": [12, 13, 14, 16, 17, 18, 19, 20, 21, 22],
      "on_demand_stages": [15]
    },
    "validation_targets": {
      "card_sharing": true,
      "determinism": true,
      "unidirectional_flow": true,
      "snapshot_count": 10,
      "clone_isolation": true,
      "worker_protocol": "postMessage only"
    }
  }
}
```

### Output Contract
```json
{
  "architecture_simulation_output": {
    "pipeline_stages_executed": 23,
    "card_sharing": {
      "status": "PASS",
      "detail": "SHARED stages computed 1x, shared to 3 clones"
    },
    "determinism": {
      "status": "PASS",
      "detail": "2-run checksum identical",
      "hash_1": "a1b2c3d4...",
      "hash_2": "a1b2c3d4..."
    },
    "unidirectional_flow": {
      "status": "PASS",
      "detail": "No backward loops detected"
    },
    "snapshot_validation": {
      "status": "PASS",
      "detail": "10 snapshots per closed candle",
      "w_fields_frozen": true,
      "od_fields_deterministic": true
    },
    "clone_isolation": {
      "status": "PASS",
      "detail": "3 sub-ledgers isolated, no stat mixing"
    },
    "worker_validation": {
      "status": "PASS",
      "detail": "All workers use postMessage, no direct IndexedDB"
    },
    "overall_verdict": "PASS"
  }
}
```

### Generated Artifact
`ArchitectureValidationResult` — immutable card, lineage to pipeline_run

### Consumer
- GOVERNANCE (Build Validation)
- AUDIT (Pipeline Audit)
- DASHBOARD (Architecture Status Panel)

### Success Criteria
- 23/23 stages executed in order
- Card sharing verified (SHARED 1x, PER-CLONE 3x)
- Determinism verified (2-run identical)
- No backward loops detected
- 10 snapshots per SP
- Clone sub-ledgers isolated

### Failure Criteria
- Any stage skipped or wrong type
- Card sharing violated (SHARED inside clone loop)
- Determinism mismatch
- Backward loop detected
- Snapshot count != 10
- Worker accessing IndexedDB directly

---

## 2. MARKET POSSIBILITY SIMULATOR

### Purpose
Mensimulasikan seluruh kemungkinan market yang dihasilkan Prediction Layer dan memvalidasi akurasinya terhadap data historis.

### Input Contract
```json
{
  "market_possibility_simulation_input": {
    "prediction_package": "dict — from PHASE-12",
    "knowledge_package": "dict — from PHASE-11",
    "structure_package": "dict — from PHASE-08",
    "historical_data": {
      "candles": "list — market data timeline",
      "snapshots": "list — historical snapshots"
    },
    "scenarios": ["BREAKOUT_UP", "CONTINUATION", "REVERSAL", "FAKE_BREAKOUT"]
  }
}
```

### Output Contract
```json
{
  "market_possibility_simulation_output": {
    "scenarios_tested": 5,
    "accuracy": {
      "breakout_up": {"predicted": 0.82, "actual": 0.78, "error": 0.04},
      "continuation": {"predicted": 0.12, "actual": 0.15, "error": -0.03},
      "reversal": {"predicted": 0.04, "actual": 0.05, "error": -0.01},
      "fake_breakout": {"predicted": 0.02, "actual": 0.02, "error": 0.00}
    },
    "overall_accuracy": 0.91,
    "calibration_quality": "GOOD — within CERMIN tolerance",
    "oi_contribution": {
      "boost_accuracy": 0.78,
      "without_oi_accuracy": 0.71,
      "oi_value_added": 0.07
    },
    "verdict": "PASS"
  }
}
```

### Generated Artifact
`MarketPossibilitySimulationResult` — immutable card

### Consumer
- PREDICTION (calibration feedback)
- KNOWLEDGE (CERMIN update)
- DASHBOARD (Prediction Accuracy Panel)

### Success Criteria
- Prediction accuracy within CERMIN tolerance
- OI dimensions improve accuracy
- No systematic over/under confidence
- All scenarios tested

### Failure Criteria
- Prediction accuracy < 50%
- Systematic bias detected (always overconfident)
- OI dimensions decrease accuracy
- CERMIN error > 20%

---

## 3. MARKET PUSH SIMULATOR

### Purpose
Mensimulasikan perjalanan market dari phase awal hingga phase akhir dan memvalidasi bagaimana ST-LMS merespons perubahan market (phase transition, breakout, reversal).

### Input Contract
```json
{
  "market_push_simulation_input": {
    "start_phase": "SIDEWAY_COMPRESSION",
    "push_scenarios": [
      {"target_phase": "BREAKOUT_UP", "probability": 0.82},
      {"target_phase": "CONTINUATION_RANGE", "probability": 0.12},
      {"target_phase": "REVERSAL_DOWN", "probability": 0.04},
      {"target_phase": "FAKE_BREAKOUT", "probability": 0.02}
    ],
    "transition_rules": "dict — phase transition matrix from BAG",
    "market_data_timeline": "list — full candle sequence"
  }
}
```

### Output Contract
```json
{
  "market_push_simulation_output": {
    "scenarios": [
      {
        "from_phase": "SIDEWAY_COMPRESSION",
        "to_phase": "BREAKOUT_UP",
        "stlms_response": {
          "schema_switch": "GRID_COMPRESSION -> LONG_BREAKOUT",
          "response_time_candles": 3,
          "response_quality": "CORRECT",
          "confidence_adjustment": "+5 (breakout confirmed)"
        }
      }
    ],
    "phase_transition_handling": {
      "correct_transitions": 18,
      "incorrect_transitions": 2,
      "delayed_transitions": 3,
      "overall_score": 0.85
    },
    "schema_switch_accuracy": 0.90,
    "verdict": "PASS"
  }
}
```

### Generated Artifact
`MarketPushSimulationResult` — immutable card

### Consumer
- TRADING SCHEMA (schema switch validation)
- KNOWLEDGE (phase transition learning)
- DASHBOARD (Market Push Panel)

### Success Criteria
- Correct schema switch on phase change
- Response time <= 5 candles
- No false schema activation
- Phase transition handling > 80%

### Failure Criteria
- Wrong schema activated on phase change
- Response time > 20 candles (too slow)
- False schema activation > 30%
- Phase transition handling < 50%

---

## 4. KNOWLEDGE SIMULATOR

### Purpose
Mensimulasikan Recommendation Package terhadap seluruh Knowledge Layer, Historical Pattern, Market Biography, dan Market DNA — memvalidasi konsistensi pengetahuan.

### Input Contract
```json
{
  "knowledge_simulation_input": {
    "recommendation_package": "dict — from PHASE-15",
    "knowledge_package": "dict — from PHASE-11",
    "historical_patterns": "list — from BAG sequence_analysis",
    "market_biography": "dict — from KNOWLEDGE.River chronicle",
    "market_dna": "dict — symbol-level pattern from BAG",
    "validation_targets": {
      "pattern_match_quality": true,
      "biography_consistency": true,
      "character_stability": true
    }
  }
}
```

### Output Contract
```json
{
  "knowledge_simulation_output": {
    "pattern_match_quality": {
      "score": 0.82,
      "detail": "82% match with historical COMPRESSION_BREAKOUT patterns"
    },
    "biography_consistency": {
      "score": 0.91,
      "detail": "Consistent with 3rd compression cycle narrative"
    },
    "character_stability": {
      "score": 0.87,
      "detail": "MEAN_REVERSION profile stable over last 50 candles"
    },
    "dna_validation": {
      "match": true,
      "detail": "BTCUSDT DNA confirms breakout tendency after compression"
    },
    "librarian_status_check": {
      "mature_patterns": 12,
      "trusted_patterns": 8,
      "deprecated_patterns": 1,
      "dead_patterns": 0
    },
    "overall_knowledge_score": 0.87,
    "verdict": "PASS"
  }
}
```

### Generated Artifact
`KnowledgeSimulationResult` — immutable card

### Consumer
- KNOWLEDGE (Librarian update, Darwin proposals)
- RECOMMENDATION (confidence adjustment)
- DASHBOARD (Knowledge Score Panel)

### Success Criteria
- Pattern match quality > 70%
- Biography consistency > 80%
- Character stability > 80%
- DNA match confirmed

### Failure Criteria
- Pattern match quality < 40%
- Biography inconsistent (contradicts chronicle)
- Character unstable (frequent profile changes)
- DNA mismatch

---

## 5. BALANCE SIMULATOR

### Purpose
Mensimulasikan hasil akhir performa balance — memproses market data dari awal hingga akhir, menjalankan seluruh pipeline, dan melihat hasil akhir balance, risk, profile, dan strategy performance.

### Input Contract
```json
{
  "balance_simulation_input": {
    "symbol": "BTCUSDT",
    "start_time_ms": 1753500000000,
    "end_time_ms": 1753586400000,
    "initial_balance": 100.0,
    "quote_asset": "USDT",
    "strategies": ["GRID_COMPRESSION", "LONG_BREAKOUT"],
    "config_override": {},
    "simulate_trades": true
  }
}
```

### Output Contract
```json
{
  "balance_simulation_output": {
    "summary": {
      "initial_balance": 100.0,
      "final_balance": 103.47,
      "absolute_pnl": 3.47,
      "percentage_pnl": 3.47,
      "candles_processed": 1440
    },
    "trades": {
      "total": 12,
      "wins": 8,
      "losses": 4,
      "win_rate": 66.7,
      "avg_win": 0.85,
      "avg_loss": -0.48,
      "profit_factor": 2.1,
      "expectancy": 0.029
    },
    "risk_metrics": {
      "max_drawdown_pct": -2.1,
      "max_drawdown_duration_candles": 45,
      "sharpe_estimate": 1.8,
      "sortino_estimate": 2.3,
      "var_95": -1.2
    },
    "strategy_performance": {
      "GRID_COMPRESSION": {"trades": 8, "win_rate": 75.0, "pnl": 2.8},
      "LONG_BREAKOUT": {"trades": 4, "win_rate": 50.0, "pnl": 0.67}
    },
    "equity_curve": [
      {"candle": 0, "balance": 100.0},
      {"candle": 100, "balance": 101.2},
      {"candle": 1440, "balance": 103.47}
    ],
    "verdict": "PASS"
  }
}
```

### Generated Artifact
`BalanceSimulationResult` — immutable card

### Consumer
- CONSUMER (fund evaluation)
- GOVERNANCE (performance validation)
- DASHBOARD (Equity Curve, Performance Panel)

### Success Criteria
- Balance computed correctly
- P&L matches sum of trade nets
- Drawdown tracked accurately
- All strategies evaluated

### Failure Criteria
- Balance mismatch (P&L != sum of trades)
- Negative expectancy across all strategies
- Drawdown > 50%
- Zero trades (strategy never activates)

---

## SIMULATION SUMMARY

```
┌──────────────────────────────────────────────────────────────────┐
│                    SIMULATION LAYER — 5 SIMULATORS                 │
│                                                                    │
│  #  Simulator                  Purpose                    Consumer │
│  ── ───────────────────────── ───────────────────────── ───────── │
│  1  Architecture Simulator    Validate pipeline           AUDIT   │
│  2  Market Possibility Sim    Validate predictions       PREDICT │
│  3  Market Push Simulator     Test phase transitions     SCHEMA  │
│  4  Knowledge Simulator       Validate knowledge         KNOWLEDGE│
│  5  Balance Simulator         Simulate P&L               CONSUMER│
│                                                                    │
│  All simulators produce immutable SimulationResult cards.         │
│  All simulators feed into Recommendation confidence.              │
│  All simulators can run in parallel (cold workers).               │
└──────────────────────────────────────────────────────────────────┘
```

---

## CONTRACT STATUS: FROZEN

Simulation Layer memiliki 5 simulator dengan input/output contract yang jelas. Phase-16 implementation mengacu pada contract ini.
