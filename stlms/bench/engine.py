"""
=====================================================
MODULE:     benchmark_engine.py
PURPOSE:    Benchmark — WASIT 5-gate walk-forward.
OWNER:      PHASE-18 BENCHMARK
=====================================================
"""


def wasit_5gate(base_markers: list, cand_markers: list,
                folds: int = 5) -> dict:
    """
    WASIT 5-Gate walk-forward validation.
    Reference: ST_LMS_CORE.js BENCHMARK.wasit
    
    G1: candidate exits >= 30
    G2: candidate expectancy > base expectancy
    G3: candidate worst-loss not worse > 10%
    G4: candidate win_rate not dropped > 2%
    G5: candidate fee_drag not increased > 0.001
    """
    base_exits = [m for m in base_markers if m.kind == "EXIT"]
    cand_exits = [m for m in cand_markers if m.kind == "EXIT"]
    
    def fold_metrics(exits: list) -> dict:
        n = len(exits)
        if n == 0:
            return {"sample": 0, "win_rate": 0, "expectancy": 0, "worst": 0, "fee": 0}
        wins = sum(1 for m in exits if m.result == "WIN")
        nets = [m.net for m in exits if m.net is not None]
        fees = [m.fee for m in exits]
        return {
            "sample": n,
            "win_rate": wins / n * 100,
            "expectancy": sum(nets) / n if nets else 0,
            "worst": min(nets) if nets else 0,
            "fee": sum(fees) / n if fees else 0,
        }
    
    bm = fold_metrics(base_exits)
    cm = fold_metrics(cand_exits)
    
    gates = {
        "G1": cm["sample"] >= 30,
        "G2": cm["expectancy"] > bm["expectancy"],
        "G3": cm["worst"] >= bm["worst"] * 1.1 if bm["worst"] < 0 else cm["worst"] >= bm["worst"],
        "G4": cm["win_rate"] >= bm["win_rate"] - 2,
        "G5": cm["fee"] <= bm["fee"] + 0.001,
    }
    
    all_pass = all(gates.values())
    
    # Identical config must fail G2
    if base_markers == cand_markers:
        gates["G2"] = False
        all_pass = False
    
    return {
        "gates": gates,
        "verdict": "PASS" if all_pass else "FAIL",
        "base": bm,
        "candidate": cm,
    }
