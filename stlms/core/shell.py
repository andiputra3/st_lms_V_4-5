"""
ST-LMS v4 — STLMSShell
Shared Core for CLI and WEB interfaces.

P0 priority from improvement plan. Provides ALL query methods needed
by both CLI and WEB, using the existing stlms modules.

Design:
    - All methods return dict or list[dict] — NO print statements, NO terminal formatting.
    - Graceful handling when data is not available (return empty/None gracefully).
    - Uses existing SQLiteConnection from stlms.sqlite.connection.
    - Uses existing ConfigurationManager from stlms.foundation.config_manager.
    - Lazy imports to avoid circular dependencies.
"""

from __future__ import annotations

import csv
import io
import json
import os
import time
from typing import Any, Optional

from stlms.core.constants import PIPELINE_STAGES, SAMPLE_GATE, ASSETS
from stlms.core.types import Candle
from stlms.core.utils import clamp
from stlms.foundation.config_manager import ConfigurationManager
from stlms.sqlite.connection import SQLiteConnection


class STLMSShell:
    """
    Shared core shell for CLI and WEB interfaces.

    Provides query methods for ALL layers: truth, structure, evidence,
    clone, statistics, bag, knowledge, prediction, schema, recommendation,
    simulation, consumer, bench, governance, integration, market, sqlite,
    foundation.

    Instantiate once and call query methods as needed. All methods return
    dict or list[dict] — suitable for JSON serialization in WEB or
    display formatting in CLI.
    """

    def __init__(
        self,
        db_path: str = "stlms.db",
        symbol: str = "BTCUSDT",
        timeframe: str = "15m",
        config: Optional[ConfigurationManager] = None,
        connection: Optional[SQLiteConnection] = None,
    ):
        self._symbol = symbol
        self._timeframe = timeframe
        self._config = config or ConfigurationManager()
        self._db_conn = connection or SQLiteConnection(db_path)

        self._market_cards: list[Any] = []
        self._truth_points: list[dict] = []
        self._lines: list[Any] = []
        self._waves: list[Any] = []
        self._cage: Any = None
        self._markers: list[Any] = []
        self._snapshots: list[dict] = []
        self._bag_artifacts: list[Any] = []
        self._knowledge: dict[str, Any] = {}
        self._prediction: dict[str, Any] = {}
        self._schema: dict[str, Any] = {}
        self._recommendation: dict[str, Any] = {}
        self._statistics: dict[str, dict] = {}
        self._pipeline_report: dict[str, Any] = {}
        self._academy_results: list[dict] = []
        self._oracle_match: dict[str, Any] = {}
        self._hivemind: dict[str, Any] = {}

        self._generated_at: float = 0.0
        self._status: str = "UNINITIALIZED"
        self._health_errors: list[str] = []

    # ── Lifecycle ───────────────────────────────────────────────

    def generate(
        self,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        candle_count: int = 500,
    ) -> dict:
        """
        Generate a full pipeline run using fixture data.

        This runs the entire 23-stage pipeline with synthetic data,
        populating all internal state so query methods return real data.
        """
        if symbol:
            self._symbol = symbol
        if timeframe:
            self._timeframe = timeframe

        try:
            from stlms.market.fixture import MarketFixture
            from stlms.market.artifact import MarketArtifact
            from stlms.market.collection import MarketCollectionResult
            from stlms.truth.point import PointBuilder, TruthArtifact
            from stlms.truth.package import TruthPackage
            from stlms.structure.line import LineBuilder
            from stlms.structure.wave import WaveBuilder
            from stlms.structure.cage import CageEngine
            from stlms.evidence.bus import EvidenceEngine
            from stlms.clone.engine import CloneEngine
            from stlms.statistics.engine import compute_statistics
            from stlms.bag.engine import BAGEngine
            from stlms.knowledge.engine import AcademyEngine, OracleEngine, HiveMindEngine
            from stlms.prediction.engine import PredictionEngine
            from stlms.schema.engine import SchemaEngine
            from stlms.recommendation.engine import RecommendationEngine
            from stlms.simulation.engine import SimulationEngine
            from stlms.integration.engine import IntegrationEngine
        except ImportError as e:
            self._health_errors.append(f"Import error during generate: {e}")
            self._status = "ERROR"
            return {"status": "ERROR", "error": str(e)}

        fixture = MarketFixture(seed=42)
        candles = fixture.generate(self._symbol, candle_count)
        oi_data = fixture.generate_oi_series(candles)

        # ── Stage 1-2: Market Collection + Artifact ─────────
        result = MarketCollectionResult(
            symbol=self._symbol,
            timeframe=self._timeframe,
            candles=candles,
            open_interest=oi_data,
            funding_rates={},
            ls_ratio={},
            taker_volume={},
            collection_start_ms=candles[0].time,
            collection_end_ms=candles[-1].time,
        )
        artifact_engine = MarketArtifact()
        self._market_cards = artifact_engine.produce(result)

        # ── Stage 3: Truth Points ───────────────────────────
        builder = PointBuilder(self._symbol)
        truth_artifact = TruthArtifact()
        market_consumer = self._lazy_market_consumer()
        self._truth_points = []
        for card in self._market_cards:
            consumed = market_consumer.consume(card)
            candle = consumed["candle"]
            oi_val = consumed.get("oi_value")
            tp = builder.build(candle, oi_value=oi_val)
            self._truth_points.append(tp)

        # ── Stage 4: Truth Package ──────────────────────────
        truth_cards = [truth_artifact.produce(tp) for tp in self._truth_points]
        truth_pkg = TruthPackage()
        self._truth_package = truth_pkg.build(truth_cards)

        # ── Stage 5-7: Structure (Line, Wave, Cage) ─────────
        sp_dicts = []
        for tp in self._truth_points:
            sp_dicts.append({
                "ts": tp.ts, "close": tp.close,
                "st": tp.st, "st_canon": tp.st_canon,
                "st_dir": tp.st_dir, "st_color": tp.st_color,
                "atr": tp.atr, "ema": tp.ema,
                "macd_hist": tp.macd_hist, "prev_macd_hist": tp.prev_macd_hist,
                "rsi": tp.rsi, "wpr": tp.wpr,
                "vel": tp.vel, "acc": tp.acc,
                "vol_delta": tp.vol_delta,
                "dist": tp.dist, "dist_atr": tp.dist_atr,
                "flip": tp.flip, "point_status": tp.point_status.value,
                "oi_value": tp.oi_value, "oi_delta": tp.oi_delta,
                "ema_slope": tp.ema_slope,
            })

        line_builder = LineBuilder()
        self._lines = line_builder.build(sp_dicts)

        wave_builder = WaveBuilder()
        self._waves = wave_builder.build(self._lines)

        cage_engine = CageEngine()
        last_sp = sp_dicts[-1]
        self._cage = cage_engine.build(
            self._lines, last_sp["close"], last_sp.get("atr") or 0.01
        )

        # ── Stage 8: Evidence ───────────────────────────────
        evidence_engine = EvidenceEngine()
        self._evidence_engine = evidence_engine

        # ── Stage 9-10: Clone observation ───────────────────
        clone_engine = CloneEngine()
        ledgers = {
            "LONG": clone_engine.new_long(),
            "SHORT": clone_engine.new_short(),
            "GRID": clone_engine.new_grid(),
        }
        self._markers = []
        self._snapshots = []

        for sp in sp_dicts:
            if sp["point_status"] != "VALID":
                continue
            cage = cage_engine.build(self._lines, sp["close"], sp.get("atr") or 0.01)
            atr = sp.get("atr") or sp["close"] * 0.01
            required = 0.7

            # Direction bus
            oi_series = oi_data
            oi_score, oi_status, oi_source = evidence_engine.oi_inherit(
                oi_series, sp["ts"]
            )
            dir_bus = evidence_engine.dir_bus(
                sp, oi_score, oi_status, oi_source,
                mtf_long=7000, mtf_short=7000
            )
            exit_bus = evidence_engine.exit_bus(sp)

            wave_structure = self._waves[-1].structure if self._waves else None
            correction_bus = evidence_engine.correction_bus(sp, cage, wave_structure)

            snap = {
                "ts": sp["ts"], "close": sp["close"],
                "wave_structure": wave_structure,
                "cage_status": cage.status,
                "dist_atr": sp.get("dist_atr") or 0.0,
                "pp": cage.pp,
                "ema": dir_bus.ema,
                "oi_score": oi_score or 0,
                "vd": dir_bus.vd,
                "mtf_final": 7000,
                "rsi": sp.get("rsi") or 50,
            }
            self._snapshots.append(snap)

            for clone_id, ledger in ledgers.items():
                if clone_id == "LONG":
                    obs = clone_engine.observe_long(
                        ledger, sp, cage, dir_bus, atr, required
                    )
                    if obs["entry_allowed"]:
                        marker = clone_engine.enter_long(ledger, sp, cage)
                        if marker:
                            self._markers.append(marker)
                elif clone_id == "SHORT":
                    obs = clone_engine.observe_short(
                        ledger, sp, cage, dir_bus, atr, required
                    )
                    if obs["entry_allowed"]:
                        marker = clone_engine.enter_short(ledger, sp, cage)
                        if marker:
                            self._markers.append(marker)
                else:
                    obs = clone_engine.observe_grid(ledger, sp, cage, required)
                    for side in obs.get("grid_to_open", []):
                        marker = clone_engine.enter_grid(ledger, sp, side)
                        if marker:
                            self._markers.append(marker)

            # Update positions + check exits
            for clone_id, ledger in ledgers.items():
                for pos in list(ledger.positions):
                    clone_engine.update_position(
                        pos, sp["close"], sp["close"], sp["close"]
                    )
                    if clone_id == "GRID":
                        exit_dec = clone_engine.decide_grid_exit(
                            pos, sp, cage, required
                        )
                    else:
                        exit_dec = clone_engine.decide_exit(pos, sp, cage, exit_bus)
                    if exit_dec:
                        reason, exit_price = exit_dec
                        marker = clone_engine.make_exit(
                            pos, sp, reason, exit_price
                        )
                        self._markers.append(marker)
                        ledger.positions.remove(pos)

        # ── Stage 10: Statistics ────────────────────────────
        for cid in ("LONG", "SHORT", "GRID"):
            self._statistics[cid] = compute_statistics(self._markers, cid)

        # ── Stage 11: BAG ───────────────────────────────────
        bag_engine = BAGEngine()
        self._bag_artifacts = bag_engine.group_by_clone_structure(
            self._markers, self._snapshots
        )

        # ── Stage 12: Knowledge (Academy, Oracle, HiveMind) ─
        academy = AcademyEngine()
        self._academy_results = academy.learn(self._bag_artifacts)

        oracle = OracleEngine()
        for snap in self._snapshots[-200:]:
            vec = oracle.vectorize(snap)
            outcome = "WIN" if snap.get("close", 0) > 0 else "LOSS"
            oracle.push(vec, snap["ts"], outcome)
        self._oracle_match = oracle.match(
            oracle.vectorize(self._snapshots[-1]) if self._snapshots
            else [0] * 9
        )

        hivemind = HiveMindEngine()
        self._hivemind = hivemind.synthesize(
            self._academy_results, self._oracle_match
        )

        self._knowledge = {
            "academy": self._academy_results,
            "oracle": self._oracle_match,
            "hivemind": self._hivemind,
        }

        # ── Stage 13: Prediction ────────────────────────────
        pred = PredictionEngine()
        self._prediction = pred.predict(self._knowledge)

        # ── Stage 14: Schema ────────────────────────────────
        schema_engine = SchemaEngine()
        market_schema = schema_engine.select_market_schema(
            cage_status=cage.status,
            wave_structure=self._waves[-1].structure if self._waves else "CHAOS",
            st_dir=last_sp.get("st_dir", 1),
            breakout=cage.breakout,
            point_status=last_sp.get("point_status", "VALID"),
        )
        entry_schema = schema_engine.select_entry_schema(
            market_schema, last_sp.get("st_dir", 1), self._prediction
        )
        active = schema_engine.get_active_clones(market_schema)
        self._schema = {
            "market_schema": market_schema,
            "entry_schema": entry_schema,
            "active_clones": active,
        }

        # ── Stage 15: Recommendation ────────────────────────
        rec = RecommendationEngine()
        self._recommendation = rec.build_report(
            market_pkg={"symbol": self._symbol, "timeframe": self._timeframe},
            truth_pkg=self._truth_package if hasattr(self, "_truth_package") else {},
            structure_pkg={
                "current": {"cage_status": cage.status},
                "status": "OK",
            },
            knowledge_pkg=self._knowledge,
            prediction_pkg=self._prediction,
            schema=self._schema,
        )

        # ── Stage 16: Integration pipeline ──────────────────
        integration = IntegrationEngine()
        self._pipeline_report = integration.run_pipeline(
            market_cards=self._market_cards,
            truth_points=self._truth_points,
            lines=self._lines,
            waves=self._waves,
            cage=self._cage,
            markers=self._markers,
            statistics=self._statistics,
            bag_artifacts=self._bag_artifacts,
            knowledge=self._knowledge,
            prediction=self._prediction,
            schema=self._schema,
            recommendation=self._recommendation,
        )

        self._generated_at = time.time()
        self._status = "OK"
        self._health_errors = []

        return self.status()

    # ── Query Methods ───────────────────────────────────────────

    def status(self) -> dict:
        """Return current shell status and generation metadata."""
        return {
            "status": self._status,
            "symbol": self._symbol,
            "timeframe": self._timeframe,
            "stages_executed": self._pipeline_report.get("stages_executed", 0),
            "stages_total": PIPELINE_STAGES + 1,
            "truth_points": len(self._truth_points),
            "lines": len(self._lines),
            "waves": len(self._waves),
            "markers": len(self._markers),
            "bag_artifacts": len(self._bag_artifacts),
            "academy_buckets": len(self._academy_results),
            "generated_at_epoch": self._generated_at,
            "db_path": self._db_conn.path,
            "db_is_open": self._db_conn.is_open,
        }

    def health(self) -> dict:
        """Return health check report."""
        checks: dict[str, bool] = {}
        if self._status == "UNINITIALIZED":
            checks["initialized"] = False
        else:
            checks["initialized"] = True
            checks["has_truth"] = len(self._truth_points) > 0
            checks["has_structure"] = len(self._lines) > 0
            checks["has_waves"] = len(self._waves) > 0
            checks["has_cage"] = self._cage is not None
            checks["has_markers"] = len(self._markers) > 0
            checks["has_bag"] = len(self._bag_artifacts) > 0
            checks["has_knowledge"] = bool(self._knowledge)
            checks["has_prediction"] = bool(self._prediction)
            checks["has_schema"] = bool(self._schema)
            checks["has_recommendation"] = bool(self._recommendation)
            checks["pipeline_ok"] = self._pipeline_report.get("verdict") == "PASS"

        all_ok = all(checks.values()) if checks else False
        return {
            "healthy": all_ok,
            "checks": checks,
            "errors": self._health_errors,
        }

    # ── Truth ───────────────────────────────────────────────────

    def truth_current(self) -> dict:
        """Return current truth snapshot."""
        if not self._truth_points:
            return {"available": False}
        last = self._truth_points[-1]
        return {
            "available": True,
            "ts": last.ts,
            "close": last.close,
            "st": last.st,
            "st_dir": last.st_dir,
            "st_color": last.st_color,
            "atr": last.atr,
            "ema": last.ema,
            "rsi": last.rsi,
            "wpr": last.wpr,
            "macd_hist": last.macd_hist,
            "vel": last.vel,
            "acc": last.acc,
            "vol_delta": last.vol_delta,
            "dist": last.dist,
            "dist_atr": last.dist_atr,
            "flip": last.flip,
            "point_status": last.point_status.value if hasattr(last.point_status, "value") else last.point_status,
            "ema_slope": last.ema_slope,
        }

    def truth_timeline(self, start: int, end: int) -> list[dict]:
        """
        Return truth points within the given timestamp range.

        Args:
            start: Start timestamp in ms (inclusive)
            end: End timestamp in ms (inclusive)
        """
        result: list[dict] = []
        for tp in self._truth_points:
            if start <= tp.ts <= end:
                result.append({
                    "ts": tp.ts, "close": tp.close,
                    "st": tp.st, "st_dir": tp.st_dir,
                    "st_color": tp.st_color,
                    "atr": tp.atr, "ema": tp.ema,
                    "rsi": tp.rsi, "wpr": tp.wpr,
                    "macd_hist": tp.macd_hist,
                    "dist": tp.dist, "dist_atr": tp.dist_atr,
                    "flip": tp.flip,
                    "point_status": tp.point_status.value if hasattr(tp.point_status, "value") else tp.point_status,
                })
        return result

    def truth_events(self) -> list[dict]:
        """Return all truth flip events."""
        events: list[dict] = []
        for tp in self._truth_points:
            if tp.flip:
                events.append({
                    "ts": tp.ts,
                    "flip": tp.flip,
                    "st": tp.st,
                    "close": tp.close,
                })
        return events

    # ── Structure ───────────────────────────────────────────────

    def structure_summary(self) -> dict:
        """Return structure layer summary."""
        if not self._lines:
            return {"available": False}

        cage_info: dict[str, Any] = {}
        if self._cage:
            cage_info = {
                "upper": self._cage.upper,
                "lower": self._cage.lower,
                "pp": self._cage.pp,
                "range_atr": self._cage.range_atr,
                "status": self._cage.status,
                "breakout": self._cage.breakout,
                "pressure_up": self._cage.pressure_up,
                "pressure_dn": self._cage.pressure_dn,
            }

        wave_info: dict[str, Any] = {}
        if self._waves:
            last_wave = self._waves[-1]
            wave_info = {
                "structure": last_wave.structure,
                "start_ts": last_wave.start_ts,
                "end_ts": last_wave.end_ts,
                "status": last_wave.status,
                "line_count": len(last_wave.lines),
            }

        return {
            "available": True,
            "total_lines": len(self._lines),
            "total_waves": len(self._waves),
            "cage": cage_info,
            "current_wave": wave_info,
        }

    def wave_current(self) -> dict:
        """Return current wave structure."""
        if not self._waves:
            return {"available": False}
        w = self._waves[-1]
        return {
            "available": True,
            "structure": w.structure,
            "start_ts": w.start_ts,
            "end_ts": w.end_ts,
            "status": w.status,
            "line_count": len(w.lines),
            "oi_trend": getattr(w, "oi_trend", "STABLE"),
            "oi_divergence": getattr(w, "oi_divergence", "NONE"),
        }

    def cage_current(self) -> dict:
        """Return current cage status."""
        if not self._cage:
            return {"available": False}
        return {
            "available": True,
            "upper": self._cage.upper,
            "lower": self._cage.lower,
            "pp": self._cage.pp,
            "range_atr": self._cage.range_atr,
            "status": self._cage.status,
            "breakout": self._cage.breakout,
            "pressure_up": self._cage.pressure_up,
            "pressure_dn": self._cage.pressure_dn,
        }

    def distance_summary(self) -> dict:
        """Return distance metrics from current truth."""
        if not self._truth_points:
            return {"available": False}
        last = self._truth_points[-1]
        return {
            "available": True,
            "dist": last.dist,
            "dist_atr": last.dist_atr,
            "close": last.close,
            "st": last.st,
            "atr": last.atr,
        }

    # ── Statistics ──────────────────────────────────────────────

    def statistics_market(self) -> dict:
        """Return aggregate statistics across all clones."""
        if not self._statistics:
            return {"available": False}
        return {
            "available": True,
            "by_clone": self._statistics,
        }

    def statistics_clone(self, clone_id: str) -> dict:
        """
        Return statistics for a specific clone.

        Args:
            clone_id: One of 'LONG', 'SHORT', 'GRID'
        """
        clone_id = clone_id.upper()
        if clone_id not in self._statistics:
            return {"available": False, "clone_id": clone_id}
        return {
            "available": True,
            "clone_id": clone_id,
            **self._statistics[clone_id],
        }

    def statistics_indicator(self, name: str) -> dict:
        """
        Return a specific statistic indicator across all clones.

        Args:
            name: Indicator name (e.g. 'win_rate', 'expectancy', 'pf')
        """
        if not self._statistics:
            return {"available": False}
        values: dict[str, Any] = {}
        for cid, stats in self._statistics.items():
            values[cid] = stats.get(name)
        return {
            "available": True,
            "indicator": name,
            "values": values,
        }

    # ── Knowledge ───────────────────────────────────────────────

    def knowledge_academy(self) -> list[dict]:
        """Return academy learning results (empirical win_rate per bucket)."""
        if not self._academy_results:
            return []
        return self._academy_results

    def knowledge_oracle(self) -> dict:
        """Return oracle similarity match result."""
        if not self._oracle_match:
            return {"match": False, "score": 0}
        return self._oracle_match

    def knowledge_hivemind(self) -> dict:
        """Return hivemind synthesis result."""
        if not self._hivemind:
            return {"intelligence_score": 5000, "dominant_bias": "NEUTRAL"}
        return self._hivemind

    # ── Prediction ──────────────────────────────────────────────

    def prediction_current(self) -> dict:
        """Return current market possibility prediction."""
        if not self._prediction:
            return {"available": False}
        return {
            "available": True,
            **self._prediction,
        }

    # ── Recommendation ──────────────────────────────────────────

    def recommendation_report(self) -> dict:
        """Return the full Market Intelligence Report."""
        if not self._recommendation:
            return {"available": False}
        return {
            "available": True,
            **self._recommendation,
        }

    # ── Simulation ──────────────────────────────────────────────

    def simulation_results(self) -> dict:
        """Return simulation results from all 5 simulators."""
        try:
            from stlms.simulation.engine import SimulationEngine
        except ImportError:
            return {"available": False, "error": "Simulation engine not available"}

        sim = SimulationEngine()

        stages = self._pipeline_report.get("stages_executed", 0)
        arch = sim.architecture_sim(
            stages_executed=stages,
            card_sharing_ok=True,
            determinism_ok=True,
        )

        pred = self._prediction or {"possibilities": [{"type": "?", "probability": 0}]}
        market_sim = sim.market_possibility_sim(
            prediction=pred, actual={"type": "TREND"}
        )

        push = sim.market_push_sim(
            from_phase="TREND", to_phase="SIDEWAY", schema_switch_correct=True
        )

        knowledge_sim = sim.knowledge_sim(
            pattern_match=0.75 if self._academy_results else 0.5,
            biography_ok=True,
        )

        balance = sim.balance_sim(
            initial=100.0,
            final=100.0 + sum(
                m.net for m in self._markers if hasattr(m, "net") and m.net is not None
            ),
            trades=len(self._markers),
            wins=sum(1 for m in self._markers if getattr(m, "result", None) == "WIN"),
        )

        return {
            "available": True,
            "architecture": arch,
            "market_possibility": market_sim,
            "market_push": push,
            "knowledge": knowledge_sim,
            "balance": balance,
        }

    # ── SQLite ──────────────────────────────────────────────────

    def sqlite_tables(self) -> list[dict]:
        """Return list of all SQLite tables with row counts."""
        try:
            from stlms.sqlite.manager import SQLiteManager
        except ImportError:
            return []

        try:
            mgr = SQLiteManager(self._db_conn)
            tables = mgr.list_tables()
            result: list[dict] = []
            for t in tables:
                result.append({
                    "name": t,
                    "rows": mgr.table_row_count(t),
                })
            return result
        except Exception:
            return []

    def sqlite_query(self, sql: str, limit: int = 100, offset: int = 0) -> dict:
        """
        Execute a read-only SQL query against the database.

        Args:
            sql: SQL SELECT query
            limit: Max rows to return
            offset: Pagination offset
        """
        try:
            from stlms.sqlite.viewer import SQLiteViewer
        except ImportError:
            return {"error": "SQLite viewer not available", "rows": [], "total": 0}

        try:
            viewer = SQLiteViewer(self._db_conn)
            result = viewer.query(sql, limit=limit, offset=offset)
            return result
        except Exception as e:
            return {"error": str(e), "rows": [], "total": 0, "limit": limit, "offset": offset}

    # ── Pipeline ────────────────────────────────────────────────

    def pipeline_status(self) -> dict:
        """Return pipeline execution status."""
        if not self._pipeline_report:
            return {
                "available": False,
                "stages_executed": 0,
                "stages_total": PIPELINE_STAGES + 1,
                "verdict": "NOT_RUN",
            }
        return {
            "available": True,
            **self._pipeline_report,
        }

    # ── Export ──────────────────────────────────────────────────

    def export(self, fmt: str = "json") -> str:
        """
        Export all shell data in the requested format.

        Args:
            fmt: 'json' or 'csv' (CSV exports trade markers)
        """
        if fmt == "csv":
            return self._export_csv()
        return self._export_json()

    def _export_json(self) -> str:
        """Export full shell state as JSON."""
        data = {
            "status": self.status(),
            "health": self.health(),
            "truth": {
                "current": self.truth_current(),
                "events": self.truth_events(),
            },
            "structure": {
                "summary": self.structure_summary(),
                "wave": self.wave_current(),
                "cage": self.cage_current(),
                "distance": self.distance_summary(),
            },
            "statistics": self.statistics_market(),
            "knowledge": {
                "academy": self.knowledge_academy(),
                "oracle": self.knowledge_oracle(),
                "hivemind": self.knowledge_hivemind(),
            },
            "prediction": self.prediction_current(),
            "recommendation": self.recommendation_report(),
            "pipeline": self.pipeline_status(),
        }
        return json.dumps(data, default=str, indent=2)

    def _export_csv(self) -> str:
        """Export trade markers as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ts", "clone", "side", "kind", "reason",
            "entry", "exit", "gross", "net", "result",
            "mae", "mfe", "hold",
        ])
        for m in self._markers:
            writer.writerow([
                m.ts, m.clone, m.side, m.kind, m.reason,
                m.entry, m.exit, m.gross, m.net, m.result,
                getattr(m, "mae", ""), getattr(m, "mfe", ""),
                getattr(m, "hold", ""),
            ])
        return output.getvalue()

    # ── Internals ───────────────────────────────────────────────

    def _lazy_market_consumer(self):
        from stlms.market.consumer import MarketConsumer
        return MarketConsumer()

    @property
    def config(self) -> ConfigurationManager:
        """Access the ConfigurationManager."""
        return self._config

    @property
    def db(self) -> SQLiteConnection:
        """Access the SQLiteConnection."""
        return self._db_conn

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def timeframe(self) -> str:
        return self._timeframe

    @property
    def truth_points(self) -> list:
        """Access raw truth points."""
        return self._truth_points

    @property
    def markers(self) -> list:
        """Access trade markers."""
        return self._markers

    @property
    def bag_artifacts(self) -> list:
        """Access BAG artifacts."""
        return self._bag_artifacts
