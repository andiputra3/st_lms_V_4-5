#!/usr/bin/env python3
"""
=====================================================
ST-LMS v3 — Full Pipeline Runner
=====================================================
Menjalankan seluruh 23-stage pipeline dari Market
Collection sampai Market Intelligence Report.
=====================================================
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stlms.market.fixture import MarketFixture
from stlms.market.artifact import MarketArtifact
from stlms.market.package import MarketPackage
from stlms.market.validator import MarketValidator
from stlms.market.consumer import MarketConsumer
from stlms.market.collection import MarketCollectionResult
from stlms.truth.point import PointBuilder, TruthArtifact
from stlms.truth.package import TruthPackage
from stlms.truth.validator import TruthValidator
from stlms.truth.consumer import TruthConsumer
from stlms.structure.line import LineBuilder
from stlms.structure.wave import WaveBuilder
from stlms.structure.cage import CageEngine
from stlms.evidence.bus import EvidenceEngine
from stlms.clone.engine import CloneEngine
from stlms.statistics.engine import compute_statistics
from stlms.bag.engine import BAGEngine
from stlms.knowledge.engine import (AcademyEngine, OracleEngine, HiveMindEngine,
                                     LibrarianEngine, DarwinEngine)
from stlms.prediction.engine import PredictionEngine
from stlms.schema.engine import SchemaEngine
from stlms.recommendation.engine import RecommendationEngine
from stlms.simulation.engine import SimulationEngine
from stlms.consumer.engine import ConsumerEngine
from stlms.bench.engine import wasit_5gate
from stlms.governance.engine import GovernanceEngine
from stlms.integration.engine import IntegrationEngine
from stlms.foundation.config_manager import ConfigurationManager


def run_pipeline(symbol: str = "BTCUSDT", candles_count: int = 200, seed: int = 42):
    """Jalankan seluruh ST-LMS pipeline."""
    
    print("=" * 60)
    print(f"  ST-LMS v3 — Full Pipeline Run")
    print(f"  Symbol: {symbol} | Candles: {candles_count} | Seed: {seed}")
    print("=" * 60)
    
    # ── Phase 01-02: Market Collection + Artifact ─────────────
    print("\n[Phase 01-02] Market Collection + Artifact...")
    fixture = MarketFixture(seed)
    candles = fixture.generate(symbol, candles_count)
    oi = fixture.generate_oi_series(candles)
    
    artifact = MarketArtifact()
    result = MarketCollectionResult(
        symbol=symbol, timeframe="1m", candles=candles,
        open_interest=oi, funding_rates={}, ls_ratio={}, taker_volume={},
        collection_start_ms=candles[0].time, collection_end_ms=candles[-1].time, gaps=[]
    )
    market_cards = artifact.produce(result)
    print(f"  Market cards: {len(market_cards)}")
    
    # ── Phase 03-04: Supertrend Point + Truth ─────────────────
    print("\n[Phase 03-04] Supertrend Point + Truth...")
    builder = PointBuilder(symbol)
    truth_artifact = TruthArtifact()
    truth_cards = []
    for c in candles:
        tp = builder.build(c)
        truth_cards.append(truth_artifact.produce(tp))
    print(f"  Truth cards: {len(truth_cards)}")
    print(f"  Last SP: close={tp.close:.1f}, st={tp.st:.1f}, dir={tp.st_dir}, "
          f"rsi={tp.rsi}, wpr={tp.wpr}, dist_atr={tp.dist_atr:.3f}")
    
    # ── Phase 05-08: Line, Wave, Cage, Evidence ───────────────
    print("\n[Phase 05-08] Structure + Evidence...")
    
    # Rebuild properly for line/wave
    builder2 = PointBuilder(symbol)
    all_points = []
    for c in candles:
        all_points.append(builder2.build(c))
    
    points_data = [{"ts": p.ts, "st": p.st, "st_canon": p.st_canon,
                    "color": p.st_color, "oi_value": p.oi_value} for p in all_points]
    
    line_builder = LineBuilder()
    lines = line_builder.build(points_data)
    
    wave_builder = WaveBuilder()
    waves = wave_builder.build(lines)
    
    cage_engine = CageEngine()
    last_candle = candles[-1]
    last_point = all_points[-1]
    cage = cage_engine.build(lines, last_candle.close, last_point.atr or 1.0)
    
    evidence = EvidenceEngine()
    _, oi_status, oi_source = evidence.oi_inherit(oi, last_point.ts)
    sector, mtf_long, mtf_short = evidence.mtf_sector(
        waves[-1].structure if waves else "CHAOS", last_point.st_dir)
    
    sp_dict = {
        "ts": last_point.ts, "close": last_point.close,
        "st_dir": last_point.st_dir, "atr": last_point.atr,
        "ema_slope": last_point.ema_slope, "vol_delta": last_point.vol_delta,
        "rsi": last_point.rsi, "wpr": last_point.wpr,
        "vel": last_point.vel, "acc": last_point.acc,
        "macd_hist": last_point.macd_hist,
        "prev_macd_hist": last_point.prev_macd_hist,
        "dist_atr": last_point.dist_atr,
    }
    
    oi_score, oi_status, oi_source = evidence.oi_inherit(oi, last_point.ts)
    dir_bus = evidence.dir_bus(sp_dict, oi_score, oi_status, oi_source, mtf_long, mtf_short)
    exit_bus = evidence.exit_bus(sp_dict)
    correction_bus = evidence.correction_bus(sp_dict, cage, waves[-1].structure if waves else None)
    
    print(f"  Lines: {len(lines)} | Waves: {len(waves)}")
    print(f"  Cage: {cage.status} | Breakout: {cage.breakout}")
    if waves:
        print(f"  Wave: {waves[-1].structure} | OI: {waves[-1].oi_trend}")
    
    # ── Phase 09-11: Clone, Trade, Position ──────────────────
    print("\n[Phase 09-11] Clone + Trade + Position...")
    clone_engine = CloneEngine()
    long_ledger = clone_engine.new_long()
    short_ledger = clone_engine.new_short()
    grid_ledger = clone_engine.new_grid()
    
    markers = []
    required_move = 0.7
    
    # Simulate trading on last candle
    long_obs = clone_engine.observe_long(long_ledger, sp_dict, cage, dir_bus,
                                          last_point.atr or 500, required_move)
    short_obs = clone_engine.observe_short(short_ledger, sp_dict, cage, dir_bus,
                                           last_point.atr or 500, required_move)
    grid_obs = clone_engine.observe_grid(grid_ledger, sp_dict, cage, required_move)
    
    if long_obs["entry_allowed"]:
        m = clone_engine.enter_long(long_ledger, sp_dict, cage)
        if m: markers.append(m)
    if short_obs["entry_allowed"]:
        m = clone_engine.enter_short(short_ledger, sp_dict, cage)
        if m: markers.append(m)
    for side in grid_obs.get("grid_to_open", []):
        m = clone_engine.enter_grid(grid_ledger, sp_dict, side)
        if m: markers.append(m)
    
    print(f"  LONG: entry_allowed={long_obs['entry_allowed']}, reason={long_obs.get('no_entry_reason', 'N/A')}")
    print(f"  SHORT: entry_allowed={short_obs['entry_allowed']}, reason={short_obs.get('no_entry_reason', 'N/A')}")
    print(f"  GRID: active={grid_obs.get('grid_active')}, fills={grid_obs.get('grid_fills')}")
    print(f"  Markers: {len(markers)}")
    
    # ── Phase 10-11: Statistics + BAG ─────────────────────────
    print("\n[Phase 10-11] Statistics + BAG...")
    stats = {
        "LONG": compute_statistics(markers, "LONG"),
        "SHORT": compute_statistics(markers, "SHORT"),
        "GRID": compute_statistics(markers, "GRID"),
    }
    
    # Create some snapshots for BAG
    snapshots = [{"ts": m.ts, "wave_structure": waves[-1].structure if waves else "CHAOS",
                  "dist_atr": last_point.dist_atr} for m in markers]
    bag_engine = BAGEngine()
    bag_artifacts = bag_engine.group_by_clone_structure(markers, snapshots)
    print(f"  BAG artifacts: {len(bag_artifacts)}")
    
    # ── Phase 11: Knowledge ──────────────────────────────────
    print("\n[Phase 11] Knowledge...")
    academy = AcademyEngine()
    oracle = OracleEngine()
    hivemind = HiveMindEngine()
    librarian = LibrarianEngine()
    darwin = DarwinEngine()
    
    academy_results = academy.learn(bag_artifacts)
    
    snap_for_oracle = {
        "wave_structure": waves[-1].structure if waves else "CHAOS",
        "cage_status": cage.status,
        "pp": cage.pp,
        "ema": dir_bus.ema,
        "oi_score": oi_score or 0,
        "vd": dir_bus.vd,
        "mtf_final": mtf_long,
        "rsi": last_point.rsi or 50,
        "dist_atr": last_point.dist_atr or 1.0,
    }
    oracle.push(oracle.vectorize(snap_for_oracle), last_point.ts, "BULLISH")
    oracle_match = oracle.match(oracle.vectorize(snap_for_oracle))
    
    hivemind_result = hivemind.synthesize(academy_results, oracle_match)
    librarian_events = librarian.evaluate(bag_artifacts)
    darwin_proposals = darwin.propose(stats)
    
    print(f"  Academy buckets: {len(academy_results)}")
    print(f"  Oracle match: {oracle_match['match']} (score: {oracle_match['score']})")
    print(f"  HiveMind: {hivemind_result['dominant_bias']} (score: {hivemind_result['intelligence_score']})")
    
    # ── Phase 12: Prediction ─────────────────────────────────
    print("\n[Phase 12] Prediction...")
    pred_engine = PredictionEngine()
    prediction = pred_engine.predict({
        "hivemind": hivemind_result,
        "academy": academy_results,
        "oracle": oracle_match,
    })
    print(f"  Bias: {prediction['dominant_bias']}")
    for p in prediction["possibilities"]:
        print(f"  {p['type']}: {p['probability']*100:.0f}% ({p['confidence']})")
    
    # ── Phase 13: Trading Schema ──────────────────────────────
    print("\n[Phase 13] Trading Schema...")
    schema_engine = SchemaEngine()
    market_schema = schema_engine.select_market_schema(
        cage.status, waves[-1].structure if waves else "CHAOS",
        last_point.st_dir, cage.breakout, last_point.point_status.value)
    entry_schema = schema_engine.select_entry_schema(market_schema, last_point.st_dir, prediction)
    active = schema_engine.get_active_clones(market_schema)
    print(f"  Market: {market_schema} | Entry: {entry_schema} | Active: {active}")
    
    # ── Phase 15: Recommendation ──────────────────────────────
    print("\n[Phase 15] Recommendation...")
    truth_pkg = TruthPackage()
    truth_report = truth_pkg.build(truth_cards)
    
    rec_engine = RecommendationEngine()
    market_pkg = MarketPackage()
    market_report = market_pkg.build(market_cards)
    
    recommendation = rec_engine.build_report(
        market_report,
        truth_report,
        {"current": {"cage_status": cage.status}, "status": "OK"},
        {"oracle": oracle_match, "hivemind": hivemind_result, "academy": academy_results},
        prediction,
        {"market_schema": market_schema, "entry_schema": entry_schema, "active_clones": active}
    )
    print(f"  Confidence: {recommendation['confidence']}/100")
    
    # ── Phase 16: Simulation ─────────────────────────────────
    print("\n[Phase 16] Simulation...")
    sim_engine = SimulationEngine()
    arch_sim = sim_engine.architecture_sim(23, True, True)
    balance_sim = sim_engine.balance_sim(100, 100 + len(markers) * 0.5, len(markers),
                                          sum(1 for m in markers if m.result == "WIN"))
    print(f"  Architecture: {arch_sim['verdict']}")
    print(f"  Balance: {balance_sim['pnl']:.2f} USDT ({balance_sim['trades']} trades)")
    
    # ── Phase 17: Consumer ────────────────────────────────────
    print("\n[Phase 17] Consumer...")
    consumer = ConsumerEngine()
    fund = consumer.fund_eval(recommendation["confidence"] * 100, 100)
    veto = consumer.veto_gate(recommendation["confidence"] * 100, "FINAL")
    intent = consumer.intent_builder(symbol, cage.status,
                                      recommendation["confidence"] * 100,
                                      last_candle.close, veto)
    print(f"  Fund: {fund['position_size']} USDT")
    print(f"  Veto: {veto['decision']}")
    print(f"  Intent: {intent['status']} ({intent.get('side', 'N/A')})")
    print(f"  Live: {'ENABLED' if consumer.live_enabled else 'DISABLED'}")
    
    # ── Phase 18: Benchmark ───────────────────────────────────
    print("\n[Phase 18] Benchmark...")
    wasit_result = wasit_5gate(markers, markers)
    print(f"  WASIT (identical): {wasit_result['verdict']} (G2={'PASS' if wasit_result['gates']['G2'] else 'FAIL'})")
    
    # ── Phase 19: Governance ──────────────────────────────────
    print("\n[Phase 19] Governance...")
    cfg = ConfigurationManager()
    gov = GovernanceEngine(cfg)
    validations = gov.validations(True, True)
    all_ok = all(v["passed"] for v in validations)
    print(f"  Validations: {'ALL PASS' if all_ok else 'SOME FAIL'}")
    
    # ── Phase 20: Integration ─────────────────────────────────
    print("\n[Phase 20] Integration...")
    integ = IntegrationEngine()
    pipeline_report = integ.run_pipeline(
        market_cards, truth_cards, lines, waves, cage,
        markers, stats, bag_artifacts,
        {"oracle": oracle_match, "hivemind": hivemind_result},
        prediction,
        {"market_schema": market_schema, "entry_schema": entry_schema, "active_clones": active},
        recommendation
    )
    print(f"  Pipeline: {pipeline_report['stages_executed']}/{pipeline_report['stages_total']} stages")
    print(f"  Verdict: {pipeline_report['verdict']}")
    
    # ── FINAL REPORT ──────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ST-LMS MARKET INTELLIGENCE REPORT")
    print("=" * 60)
    print(f"  Symbol:     {symbol}")
    print(f"  State:      {cage.status}")
    print(f"  Wave:       {waves[-1].structure if waves else 'N/A'}")
    print(f"  ST:         {last_point.st:.1f} ({last_point.st_color})")
    print(f"  Distance:   {last_point.dist_atr:.3f} ATR")
    print(f"  Prediction: {prediction['dominant_bias']}")
    for p in prediction["possibilities"]:
        print(f"    {p['type']}: {p['probability']*100:.0f}%")
    print(f"  Schema:     {entry_schema}")
    print(f"  Confidence: {recommendation['confidence']}/100")
    print(f"  Pipeline:   {pipeline_report['verdict']}")
    print("=" * 60)
    print(f"  DISCLAIMER: Market Intelligence Report.")
    print(f"  NOT a trading signal. NOT financial advice.")
    print("=" * 60)


class TruthPoint_stub:
    """Stub to avoid recomputation."""
    pass


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="ST-LMS v3 Pipeline Runner")
    p.add_argument("--symbol", default="BTCUSDT", help="Trading pair")
    p.add_argument("--candles", type=int, default=200, help="Number of candles")
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    args = p.parse_args()
    run_pipeline(args.symbol, args.candles, args.seed)
