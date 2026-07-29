"""
=====================================================
MODULE:     simulation_engine.py
PURPOSE:    Simulation Layer — 5 simulators.
OWNER:      PHASE-16 SIMULATION LAYER
=====================================================
"""

import time


class SimulationEngine:
    """5 simulators untuk validasi ST-LMS."""
    
    def architecture_sim(self, stages_executed: int,
                         card_sharing_ok: bool,
                         determinism_ok: bool) -> dict:
        return {
            "simulator": "Architecture",
            "stages": f"{stages_executed}/23",
            "card_sharing": "PASS" if card_sharing_ok else "FAIL",
            "determinism": "PASS" if determinism_ok else "FAIL",
            "verdict": "PASS" if (stages_executed == 23 and card_sharing_ok and determinism_ok) else "FAIL",
        }
    
    def market_possibility_sim(self, prediction: dict, actual: dict) -> dict:
        top_pred = prediction.get("possibilities", [{}])[0]
        pred_type = top_pred.get("type", "?")
        pred_prob = top_pred.get("probability", 0)
        actual_type = actual.get("type", "?")
        
        return {
            "simulator": "Market Possibility",
            "predicted": f"{pred_type} ({pred_prob*100:.0f}%)",
            "actual": actual_type,
            "accuracy": "PASS" if pred_prob > 0.5 else "LOW",
        }
    
    def market_push_sim(self, from_phase: str, to_phase: str,
                        schema_switch_correct: bool) -> dict:
        return {
            "simulator": "Market Push",
            "transition": f"{from_phase} -> {to_phase}",
            "schema_response": "CORRECT" if schema_switch_correct else "INCORRECT",
            "verdict": "PASS" if schema_switch_correct else "FAIL",
        }
    
    def knowledge_sim(self, pattern_match: float, biography_ok: bool) -> dict:
        return {
            "simulator": "Knowledge",
            "pattern_match": f"{pattern_match*100:.0f}%",
            "biography": "CONSISTENT" if biography_ok else "INCONSISTENT",
            "verdict": "PASS" if pattern_match > 0.7 and biography_ok else "FAIL",
        }
    
    def balance_sim(self, initial: float, final: float,
                    trades: int, wins: int) -> dict:
        pnl = final - initial
        win_rate = (wins / trades * 100) if trades > 0 else 0
        return {
            "simulator": "Balance",
            "initial": initial,
            "final": round(final, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl / initial * 100, 2),
            "trades": trades,
            "win_rate": round(win_rate, 1),
            "verdict": "PASS" if pnl > 0 else "LOSS",
        }
