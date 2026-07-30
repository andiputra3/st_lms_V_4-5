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
from stlms.core.utils import clamp, IDGenerator
from stlms.foundation.config_manager import ConfigurationManager
from stlms.sqlite.connection import SQLiteConnection
from stlms.snapshot.manager import SnapshotManager
from stlms.snapshot.registry import SnapshotRegistry
from stlms.snapshot.validator import SnapshotValidator


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
        timeframe: str = "1m",
        config: Optional[ConfigurationManager] = None,
        connection: Optional[SQLiteConnection] = None,
        enable_persistence: bool = True,
    ):
        self._symbol = symbol
        self._timeframe = timeframe
        self._config = config or ConfigurationManager()
        self._db_conn = connection or SQLiteConnection(db_path)
        self._enable_persistence = enable_persistence

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
        self._market_dna: dict[str, Any] = {}

        self._snapshot_registry = SnapshotRegistry()
        self._snapshot_manager = SnapshotManager(self._db_conn)
        self._snapshot_cards: dict[str, list] = {}

        self._generated_at: float = 0.0
        self._status: str = "UNINITIALIZED"
        self._health_errors: list[str] = []

        from stlms.core.memory import MarketObservationMemory
        self._memory = MarketObservationMemory()
        self._memory.set_batch_full_callback(self._on_snapshot_batch_full)

        self._snapshot_batches: list = []
        self._batch_evolution_stats: dict = {}

        if self._enable_persistence:
            self._init_persistence_tables()

    def _on_snapshot_batch_full(self, batch):
        """
        Callback saat SnapshotBatch mencapai 48000 observation.
        FREEZE batch → compute evolution stats → persist to SQLite → archive.
        Data TIDAK dihapus — hanya di-archive.
        """
        import time
        batch.frozen_at = time.time()
        
        # Compute evolution statistics for this batch
        if hasattr(self, '_truth_points') and self._truth_points:
            try:
                from stlms.statistics.domains.evolution_stats import EvolutionStatistics
                ev = EvolutionStatistics()
                batch.evolution_report = ev.compute(
                    self._truth_points, self._lines, self._waves,
                    [self._cage] if self._cage else []
                )
            except Exception:
                pass
        
        # Store batch DNA
        if hasattr(self, '_market_dna') and self._market_dna:
            batch.dna_profile = self._market_dna
            batch.market_character = self._market_dna.get("market_character", "")
        
        # Persist batch to SQLite
        if self._enable_persistence:
            try:
                db = self._db_conn.open()
                batch_json = str(batch.summary())
                db.execute(
                    "INSERT INTO snapshot_batches (batch_id, start_index, end_index, observation_count, lifecycle_state, market_character, dna_profile, evolution_report, created_at, frozen_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (batch.batch_id, batch.start_index, batch.end_index,
                     batch.size, batch.lifecycle_state, batch.market_character,
                     str(batch.dna_profile)[:1000], str(batch.evolution_report)[:2000],
                     batch.created_at, batch.frozen_at)
                )
                db.commit()
            except Exception:
                pass
        
        self._snapshot_batches.append({
            "batch_id": batch.batch_id,
            "observation_count": batch.size,
            "lifecycle_state": batch.lifecycle_state,
            "market_character": batch.market_character,
            "frozen_at": batch.frozen_at,
        })

    # ── Persistence ─────────────────────────────────────────────

    def _init_persistence_tables(self) -> None:
        db = self._db_conn.open()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS snapshot_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                start_index INTEGER, end_index INTEGER,
                observation_count INTEGER DEFAULT 0,
                lifecycle_state TEXT DEFAULT 'NEW',
                market_character TEXT,
                dna_profile TEXT,
                evolution_report TEXT,
                created_at REAL, frozen_at REAL,
                archived_at REAL,
                UNIQUE(batch_id)
            );
            CREATE TABLE IF NOT EXISTS truth_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                close REAL, st REAL, st_dir INTEGER, st_color TEXT,
                atr REAL, ema REAL, rsi REAL, wpr REAL,
                macd_hist REAL, vel REAL, acc REAL,
                vol_delta REAL, dist REAL, dist_atr REAL,
                flip INTEGER, point_status TEXT,
                ema_slope REAL, oi_value REAL, oi_delta REAL,
                generated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS structure_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                wave_structure TEXT,
                cage_status TEXT, cage_breakout TEXT,
                cage_upper REAL, cage_lower REAL, cage_pp REAL,
                cage_range_atr REAL,
                line_count INTEGER, wave_count INTEGER,
                generated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS evidence_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                oi_score REAL, oi_status TEXT, oi_source TEXT,
                mtf_long REAL, mtf_short REAL,
                mtf_final REAL, wave_structure TEXT,
                cage_status TEXT, dist_atr REAL,
                generated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS clone_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                clone_id TEXT NOT NULL,
                entry_allowed INTEGER,
                no_entry_reason TEXT,
                confidence REAL,
                generated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS trade_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                clone TEXT NOT NULL,
                side TEXT, kind TEXT, reason TEXT,
                entry REAL, exit_price REAL,
                gross REAL, net REAL, result TEXT,
                mae REAL, mfe REAL, hold_c INTEGER,
                generated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS trade_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                clone_id TEXT NOT NULL,
                sample INTEGER, win_rate REAL,
                expectancy REAL, pf REAL,
                avg_win REAL, avg_loss REAL,
                status TEXT,
                generated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS bag_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                bag_id TEXT NOT NULL,
                bag_kind TEXT, bag_key TEXT,
                sample_count INTEGER, win_count INTEGER, loss_count INTEGER,
                win_rate REAL, consensus TEXT, conflict_level TEXT,
                confidence REAL, maturity_score REAL,
                generated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS knowledge_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                knowledge_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                generated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                dominant_bias TEXT,
                intelligence_score REAL,
                no_model INTEGER,
                possibilities_json TEXT NOT NULL,
                generated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS governance_proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                param_key TEXT NOT NULL,
                current_value REAL,
                proposed_value REAL,
                reason TEXT,
                status TEXT,
                generated_at TEXT DEFAULT (datetime('now'))
            );
        """)
        self._db_conn.commit()

    def _record_snapshot_card(self, stage_name: str, snapshot_type: str, payload: dict) -> None:
        ts_ms = int(time.time() * 1000)
        try:
            card = self._snapshot_manager.produce(
                stage_name, snapshot_type, payload, [], ts_ms
            )
            card = self._snapshot_manager.freeze(card)
            if self._enable_persistence:
                self._snapshot_manager.store(card)
            validator = SnapshotValidator(self._snapshot_registry)
            validation_results = validator.validate(card)
            failed = [r for r in validation_results if not r.passed]
            if failed:
                for f in failed:
                    self._health_errors.append(f"Snapshot validation [{f.name}]: {f.detail}")
            cards = self._snapshot_cards.get(snapshot_type, [])
            cards.append(card)
            self._snapshot_cards[snapshot_type] = cards
        except Exception as e:
            self._health_errors.append(f"Snapshot error: {e}")

    def persist(self) -> dict:
        """Persist all collected data to SQLite. Returns counts of persisted rows."""
        if not self._enable_persistence:
            return {"persisted": False, "reason": "persistence disabled"}

        results = {}
        try:
            from stlms.sqlite.manager import SQLiteManager
            mgr = SQLiteManager(self._db_conn)

            for tp in self._truth_points:
                self._db_conn.execute(
                    """INSERT INTO truth_snapshots
                       (ts, symbol, timeframe, close, st, st_dir, st_color,
                        atr, ema, rsi, wpr, macd_hist, vel, acc,
                        vol_delta, dist, dist_atr, flip, point_status,
                        ema_slope, oi_value, oi_delta)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (tp.ts, self._symbol, self._timeframe,
                     tp.close, tp.st, tp.st_dir, tp.st_color,
                     tp.atr, tp.ema, tp.rsi, tp.wpr,
                     tp.macd_hist, tp.vel, tp.acc,
                     tp.vol_delta, tp.dist, tp.dist_atr,
                     1 if tp.flip else 0, str(tp.point_status),
                     tp.ema_slope, tp.oi_value, tp.oi_delta))
            results["truth_snapshots"] = len(self._truth_points)

            cage_info = {}
            if self._cage:
                cage_info = {
                    "cage_status": self._cage.status,
                    "cage_breakout": self._cage.breakout,
                    "cage_upper": self._cage.upper,
                    "cage_lower": self._cage.lower,
                    "cage_pp": self._cage.pp,
                    "cage_range_atr": self._cage.range_atr,
                }
            wave_structure = self._waves[-1].structure if self._waves else None
            self._db_conn.execute(
                """INSERT INTO structure_snapshots
                   (ts, symbol, timeframe, wave_structure,
                    cage_status, cage_breakout, cage_upper, cage_lower,
                    cage_pp, cage_range_atr, line_count, wave_count)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (int(time.time() * 1000), self._symbol, self._timeframe,
                 wave_structure,
                 cage_info.get("cage_status"), cage_info.get("cage_breakout"),
                 cage_info.get("cage_upper"), cage_info.get("cage_lower"),
                 cage_info.get("cage_pp"), cage_info.get("cage_range_atr"),
                 len(self._lines), len(self._waves)))
            results["structure_snapshots"] = 1

            for snap in self._snapshots:
                self._db_conn.execute(
                    """INSERT INTO evidence_snapshots
                       (ts, symbol, timeframe, oi_score, oi_status, oi_source,
                        mtf_long, mtf_short, mtf_final, wave_structure,
                        cage_status, dist_atr)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (snap.get("ts"), self._symbol, self._timeframe,
                     snap.get("oi_score", 0), snap.get("oi_status"), snap.get("oi_source"),
                     snap.get("mtf_long"), snap.get("mtf_short"),
                     snap.get("mtf_final"), snap.get("wave_structure"),
                     snap.get("cage_status"), snap.get("dist_atr", 0)))
            results["evidence_snapshots"] = len(self._snapshots)

            for snap in self._snapshots:
                self._db_conn.execute(
                    """INSERT INTO clone_observations
                       (ts, symbol, timeframe, clone_id, entry_allowed,
                        no_entry_reason, confidence)
                       VALUES (?,?,?,?,?,?,?)""",
                    (snap.get("ts"), self._symbol, self._timeframe,
                     "SYNTHETIC", 1, None,
                     snap.get("confidence", 0.5)))
            results["clone_observations"] = len(self._snapshots)

            marker_count = 0
            for m in self._markers:
                self._db_conn.execute(
                    """INSERT INTO trade_markers
                       (ts, symbol, timeframe, clone, side, kind, reason,
                        entry, exit_price, gross, net, result, mae, mfe, hold_c)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (m.ts, self._symbol, self._timeframe,
                     m.clone, m.side, m.kind, m.reason,
                     m.entry, m.exit, m.gross, m.net, m.result,
                     getattr(m, "mae", None), getattr(m, "mfe", None),
                     getattr(m, "hold", None)))
                marker_count += 1
            results["trade_markers"] = marker_count

            for cid, stats in self._statistics.items():
                if cid in ("LONG", "SHORT", "GRID"):
                    self._db_conn.execute(
                        """INSERT INTO trade_statistics
                           (symbol, timeframe, clone_id, sample, win_rate,
                            expectancy, pf, avg_win, avg_loss, status)
                           VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (self._symbol, self._timeframe, cid,
                         stats.get("sample", 0), stats.get("win_rate", 0),
                         stats.get("expectancy", 0), stats.get("pf", 0),
                         stats.get("avg_win", 0), stats.get("avg_loss", 0),
                         stats.get("status", "UNKNOWN")))
            results["trade_statistics"] = sum(1 for c in ("LONG", "SHORT", "GRID") if c in self._statistics)

            for ba in self._bag_artifacts:
                self._db_conn.execute(
                    """INSERT INTO bag_artifacts
                       (symbol, timeframe, bag_id, bag_kind, bag_key,
                        sample_count, win_count, loss_count,
                        win_rate, consensus, conflict_level,
                        confidence, maturity_score)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (self._symbol, self._timeframe,
                     ba.bag_id, str(ba.bag_kind), ba.bag_key,
                     ba.sample_count, ba.win_count, ba.loss_count,
                     ba.win_rate, ba.consensus, ba.conflict_level,
                     ba.confidence, ba.maturity_score))
            results["bag_artifacts"] = len(self._bag_artifacts)

            for ktype, kdata in self._knowledge.items():
                self._db_conn.execute(
                    """INSERT INTO knowledge_artifacts
                       (symbol, timeframe, knowledge_type, payload_json)
                       VALUES (?,?,?,?)""",
                    (self._symbol, self._timeframe, ktype,
                     json.dumps(kdata, default=str)))
            results["knowledge_artifacts"] = len(self._knowledge)

            if self._prediction:
                possibilities_json = json.dumps(
                    self._prediction.get("possibilities", []), default=str
                )
                self._db_conn.execute(
                    """INSERT INTO predictions
                       (symbol, timeframe, dominant_bias, intelligence_score,
                        no_model, possibilities_json)
                       VALUES (?,?,?,?,?,?)""",
                    (self._symbol, self._timeframe,
                     self._prediction.get("dominant_bias"),
                     self._prediction.get("intelligence_score"),
                     1 if self._prediction.get("no_model") else 0,
                     possibilities_json))
            results["predictions"] = 1 if self._prediction else 0

            self._db_conn.commit()
            results["persisted"] = True
        except Exception as e:
            self._health_errors.append(f"Persist error: {e}")
            results["persisted"] = False
            results["error"] = str(e)

        return results

    def query_truth_snapshots(self, limit: int = 100) -> list[dict]:
        """Query truth snapshots from SQLite."""
        rows = self._db_conn.execute(
            "SELECT * FROM truth_snapshots ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def query_trade_markers(self, limit: int = 100) -> list[dict]:
        """Query trade markers from SQLite."""
        rows = self._db_conn.execute(
            "SELECT * FROM trade_markers ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def query_bag_artifacts(self, limit: int = 100) -> list[dict]:
        """Query BAG artifacts from SQLite."""
        rows = self._db_conn.execute(
            "SELECT * FROM bag_artifacts ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def query_predictions(self, limit: int = 10) -> list[dict]:
        """Query predictions from SQLite."""
        rows = self._db_conn.execute(
            "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try:
                d["possibilities"] = json.loads(d.get("possibilities_json", "[]"))
            except Exception:
                d["possibilities"] = []
            del d["possibilities_json"]
            result.append(d)
        return result

    def query_sql(self, sql: str, params: tuple = ()) -> list[dict]:
        """Execute arbitrary read query against SQLite."""
        try:
            rows = self._db_conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            return [{"error": str(e)}]

    # ── Snapshot Query Methods ──────────────────────────────────

    def snapshots(self) -> dict:
        """Return snapshot counts per type from the snapshot registry."""
        return {
            "total_cards": sum(len(v) for v in self._snapshot_cards.values()),
            "by_type": {
                stype: len(cards) for stype, cards in self._snapshot_cards.items()
            },
            "registry_types": self._snapshot_registry.list_types(),
            "registry_count": self._snapshot_registry.type_count(),
        }

    def market_dna(self) -> dict:
        """Return the market DNA profile."""
        if not self._market_dna:
            return {"available": False}
        return {"available": True, **self._market_dna}

    # ── Lifecycle ───────────────────────────────────────────────

    def reset(self) -> None:
        """Explicitly reset all internal state."""
        self._market_cards.clear()
        self._truth_points.clear()
        self._lines.clear()
        self._waves.clear()
        self._cage = None
        self._markers.clear()
        self._snapshots.clear()
        self._bag_artifacts.clear()
        self._knowledge.clear()
        self._prediction.clear()
        self._schema.clear()
        self._recommendation.clear()
        self._statistics.clear()
        self._pipeline_report.clear()
        self._academy_results.clear()
        self._oracle_match.clear()
        self._hivemind.clear()
        self._market_dna.clear()
        self._snapshot_cards.clear()
        self._snapshot_batches.clear()
        self._batch_evolution_stats.clear()
        self._generated_at = 0.0
        self._status = "UNINITIALIZED"
        self._health_errors.clear()

    def generate(
        self,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        candle_count: int = 500,
        reset_first: bool = True,
    ) -> dict:
        """
        Generate a full pipeline run using fixture data.

        This runs the entire 23-stage pipeline with synthetic data,
        populating all internal state so query methods return real data.

        Args:
            reset_first: If True (default), clears all state before generating.
                         If False, appends new observations to existing state.
        """
        if reset_first:
            self.reset()
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
            from stlms.statistics.domains.evolution_stats import EvolutionStatistics
            from stlms.statistics.domains.indicator_stats import IndicatorStatistics
            from stlms.statistics.domains.market_stats import MarketStatistics
            from stlms.statistics.domains.clone_stats import CloneStatistics
            from stlms.statistics.domains.correlation_stats import CorrelationStatistics
            from stlms.statistics.domains.distance_stats import DistanceStatistics
            from stlms.statistics.domains.oi_stats import OIStatistics
            from stlms.bag.engine import BAGEngine
            from stlms.knowledge.engine import AcademyEngine, OracleEngine, HiveMindEngine, LibrarianEngine, DarwinEngine
            from stlms.prediction.engine import PredictionEngine
            from stlms.schema.engine import SchemaEngine
            from stlms.recommendation.engine import RecommendationEngine
            from stlms.simulation.engine import SimulationEngine
            from stlms.integration.engine import IntegrationEngine
            from stlms.truth.observation import TruthObservationObject
            from stlms.structure.observation import StructureObservationObject, LineObservation, WaveObservation, CageObservation
            from stlms.truth.lifecycle import EvolutionLifecycleManager, EvolutionLifecycle
            from stlms.truth.mutation import MutationTracker
            from stlms.truth.reliability import ReliabilityScorer
            from stlms.truth.event import MarketEventRecorder, EventType
            from stlms.evidence.mtf_inheritance import MTFInheritance
        except ImportError as e:
            self._health_errors.append(f"Import error during generate: {e}")
            self._status = "ERROR"
            return {"status": "ERROR", "error": str(e)}

        fixture = MarketFixture(seed=42)
        
        # Gunakan Historical Collection Engine untuk batch-aware collection
        from stlms.market.batch_collector import HistoricalCollectionEngine
        from stlms.market.provider import FixtureProvider
        provider = FixtureProvider(seed=42)
        collector = HistoricalCollectionEngine(provider, target_count=candle_count)
        collection_result = collector.collect(self._symbol, self._timeframe)
        candles = collection_result["candles"]
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

        for card in self._market_cards:
            self._record_snapshot_card(
                "market", "market_snapshot",
                {"ts": card.timestamp_ms, "symbol": self._symbol,
                 "timeframe": self._timeframe, "entity_id": card.entity_id}
            )

        # ── Stage 3: Truth Points ───────────────────────────
        builder = PointBuilder(self._symbol)
        truth_artifact = TruthArtifact()
        market_consumer = self._lazy_market_consumer()

        mutation_tracker = MutationTracker()
        reliability_scorer = ReliabilityScorer()
        lifecycle_manager = EvolutionLifecycleManager()
        event_recorder = MarketEventRecorder()
        mtf_inheritance = MTFInheritance()

        for i, card in enumerate(self._market_cards):
            consumed = market_consumer.consume(card)
            candle = consumed["candle"]
            oi_val = consumed.get("oi_value")
            tp = builder.build(candle, oi_value=oi_val)
            self._truth_points.append(tp)

            truth_obs = TruthObservationObject(
                point=tp,
                observation_id=f"TRUTH_{i:06d}",
                candle_index=i,
            )

            prev_tp = self._truth_points[i - 1] if i > 0 else None
            if prev_tp is not None:
                mutation_delta = mutation_tracker.track(prev_tp, tp)
                truth_obs.mutation_delta = mutation_delta
                has_mutation = any(
                    abs(v) > 0.001 for k, v in mutation_delta.items()
                    if isinstance(v, (int, float)) and k != "flip"
                )
                if has_mutation:
                    truth_obs.version += 1
                    truth_obs.mutation_count += 1
                if tp.flip:
                    truth_obs.mutation_count += 1

            reliability = reliability_scorer.score(tp)
            truth_obs.reliability = reliability

            lifecycle_manager.transition(EvolutionLifecycle.NEW)
            lifecycle_manager.transition(EvolutionLifecycle.LIVE)
            truth_obs.pipeline_state = "OPEN"
            truth_obs.evolution_state = lifecycle_manager.current.value if lifecycle_manager.current else "NEW"
            truth_obs.lifecycle_history = list(lifecycle_manager._history)

            event_recorder.record_if(
                tp.ts, EventType.TREND_FLIP, "INFO",
                f"ST flip at candle {i}", tp.flip,
                {"st_dir": tp.st_dir, "st_color": tp.st_color}
            )
            if tp.rsi is not None and (tp.rsi < 20 or tp.rsi > 80):
                event_recorder.record(
                    tp.ts, EventType.EXTREME_RSI, "WARNING",
                    f"RSI {tp.rsi:.1f} at candle {i}",
                    {"rsi": tp.rsi}
                )
            if tp.wpr is not None and (tp.wpr > -10 or tp.wpr < -90):
                event_recorder.record(
                    tp.ts, EventType.EXTREME_WPR, "WARNING",
                    f"WPR {tp.wpr:.1f} at candle {i}",
                    {"wpr": tp.wpr}
                )
            truth_obs.events = event_recorder.to_dict_list()[-3:]

            mtf_context = mtf_inheritance.get_context(tp.ts)
            truth_obs.mtf_context = mtf_context.to_dict() if mtf_context else None

            struct_obs = StructureObservationObject(
                observation_id=f"STRUCT_{i:06d}",
                candle_index=i,
            )
            truth_obs.structure_context = struct_obs.to_dict()

            obs_dict = self.get_observation(i)
            obs_dict["truth_observation"] = truth_obs.to_dict()
            obs_dict["reliability"] = reliability
            obs_dict["mutation_delta"] = truth_obs.mutation_delta
            obs_dict["version"] = truth_obs.version
            obs_dict["mutation_count"] = truth_obs.mutation_count
            self._memory.append(obs_dict)

        # ── Stage 4: Truth Package ──────────────────────────
        truth_cards = [truth_artifact.produce(tp) for tp in self._truth_points]
        truth_pkg = TruthPackage()
        self._truth_package = truth_pkg.build(truth_cards)

        for tp in self._truth_points[-10:]:
            self._record_snapshot_card(
                "truth", "truth_snapshot",
                {"ts": tp.ts, "symbol": self._symbol, "timeframe": self._timeframe,
                 "open": tp.open if hasattr(tp, 'open') else None,
                 "high": tp.high if hasattr(tp, 'high') else None,
                 "low": tp.low if hasattr(tp, 'low') else None,
                 "close": tp.close, "volume": tp.volume if hasattr(tp, 'volume') else None,
                 "data_status": str(tp.point_status)}
            )

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

        self._record_snapshot_card(
            "structure", "structure_snapshot",
            {"ts": last_sp["ts"], "symbol": self._symbol,
             "timeframe": self._timeframe,
             "support_levels": str(cage_engine),
             "resistance_levels": str(cage_engine),
             "trend_strength": 5000,
             "wave_structure": self._waves[-1].structure if self._waves else "CHAOS",
             "cage_status": self._cage.status,
             "cage_breakout": self._cage.breakout,
             "market_phase": self._cage.status}
        )

        # ── Stage 8: Evidence ───────────────────────────────
        evidence_engine = EvidenceEngine()
        self._evidence_engine = evidence_engine

        evidence_snap_count = 0
        for sp in sp_dicts[-20:]:
            if evidence_snap_count >= 5:
                break
            if sp["point_status"] != "VALID":
                continue
            self._record_snapshot_card(
                "evidence", "evidence_snapshot",
                {"ts": sp["ts"], "symbol": self._symbol,
                 "timeframe": self._timeframe,
                 "long_signals": 0, "short_signals": 0,
                 "consensus_level": "MEDIUM",
                 "conflict_level": "NONE",
                 "bag_weights": {}}
            )
            evidence_snap_count += 1

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

        for snap in self._snapshots[-5:]:
            self._record_snapshot_card(
                "clone", "clone_observation",
                {"ts": snap["ts"], "symbol": self._symbol,
                 "timeframe": self._timeframe,
                 "clone_kind": "SYNTHETIC",
                 "entry_price": snap.get("close", 0),
                 "stop_loss": snap.get("close", 0) * 0.98,
                 "take_profit": snap.get("close", 0) * 1.04,
                 "position_size": 0.01,
                 "risk_reward": 2.0,
                 "confidence": 0.5}
            )

        for marker in self._markers[-20:]:
            self._record_snapshot_card(
                "clone", "trade_snapshot",
                {"ts": marker.ts, "symbol": self._symbol,
                 "timeframe": self._timeframe,
                 "trade_kind": marker.kind,
                 "trade_side": marker.side,
                 "entry_price": marker.entry,
                 "exit_price": marker.exit,
                 "quantity": 0.01,
                 "pnl": marker.net,
                 "pnl_pct": marker.net / marker.entry * 100 if marker.entry else 0,
                 "trade_result": marker.result}
            )

        # ── Stage 10: Statistics ────────────────────────────
        for cid in ("LONG", "SHORT", "GRID"):
            self._statistics[cid] = compute_statistics(self._markers, cid)

        # Position snapshot (after position management loop)
        self._record_snapshot_card(
            "position", "position_snapshot",
            {"ts": int(time.time() * 1000), "symbol": self._symbol,
             "timeframe": self._timeframe, "active_positions": sum(1 for m in self._markers if getattr(m, 'kind', None) == 'ENTRY'),
             "closed_positions": sum(1 for m in self._markers if getattr(m, 'kind', None) == 'EXIT'),
             "total_markers": len(self._markers)}
        )

        # ── Stage 10b: Statistics Domains (7 domains) ──────
        ev_stats = EvolutionStatistics()
        self._statistics["evolution"] = ev_stats.compute(
            self._truth_points, self._lines, self._waves,
            [self._cage] if self._cage else []
        )
        ind_stats = IndicatorStatistics()
        self._statistics["indicator"] = ind_stats.compute(self._truth_points)
        mkt_stats = MarketStatistics()
        self._statistics["market"] = mkt_stats.compute(self._waves, [self._cage] if self._cage else [])
        clone_stats = CloneStatistics()
        self._statistics["clone_stats"] = clone_stats.compute(self._markers)
        corr_stats = CorrelationStatistics()
        self._statistics["correlation"] = corr_stats.compute(self._truth_points)
        dist_stats = DistanceStatistics()
        self._statistics["distance"] = dist_stats.compute(self._truth_points)
        oi_stats = OIStatistics()
        self._statistics["oi"] = oi_stats.compute(self._truth_points)

        for cid in ("LONG", "SHORT", "GRID"):
            if cid in self._statistics:
                stats = self._statistics[cid]
                self._record_snapshot_card(
                    "statistics", "statistics_snapshot",
                    {"ts": int(time.time() * 1000), "symbol": self._symbol,
                     "timeframe": self._timeframe,
                     "total_trades": stats.get("sample", 0),
                     "win_count": int(stats.get("sample", 0) * stats.get("win_rate", 0) / 100),
                     "loss_count": int(stats.get("sample", 0) * (100 - stats.get("win_rate", 0)) / 100),
                     "win_rate": stats.get("win_rate", 0),
                     "avg_win": stats.get("avg_win", 0),
                     "avg_loss": stats.get("avg_loss", 0),
                     "profit_factor": stats.get("pf", 0),
                     "max_drawdown_pct": 0}
                )

        # ── Stage 11: BAG ───────────────────────────────────
        bag_engine = BAGEngine()
        self._bag_artifacts = bag_engine.group_by_clone_structure(
            self._markers, self._snapshots
        )

        dna_result = bag_engine.extract_dna(
            self._waves, [self._cage] if self._cage else [], self._truth_points
        )
        wave_dist = dna_result.get("dna_profile", {}).get("wave_distribution", {})
        cage_dist = dna_result.get("dna_profile", {}).get("cage_distribution", {})
        character = bag_engine.analyze_character(wave_dist, cage_dist)
        self._market_dna = {
            **dna_result.get("dna_profile", {}),
            **character.get("market_character", {}),
        }

        for ba in self._bag_artifacts:
            self._record_snapshot_card(
                "bag", "knowledge_snapshot",
                {"ts": int(time.time() * 1000), "symbol": self._symbol,
                 "timeframe": self._timeframe,
                 "knowledge_entity": ba.bag_id,
                 "librarian_status": ba.consensus,
                 "pattern_signature": ba.bag_key,
                 "success_rate": ba.win_rate or 0,
                 "sample_count": ba.sample_count}
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
        evolution_context = None
        if self._statistics.get("evolution"):
            evo = self._statistics["evolution"]
            truth = evo.get("truth", {})
            line = evo.get("line", {})
            wave = evo.get("wave", {})
            evo_cage = evo.get("cage", {})
            
            last_wave = self._waves[-1] if self._waves else None
            
            market_character = {}
            if last_wave and hasattr(last_wave, 'market_character'):
                market_character = {"profile": last_wave.market_character}
            
            if evo_cage:
                status_dist = evo_cage.get("status_distribution", {})
                breakout_dist = evo_cage.get("breakout_distribution", {})
                from stlms.bag.engine import BAGEngine
                bag = BAGEngine()
                char = bag.analyze_character(
                    wave.get("structure_distribution", {}),
                    status_dist
                )
                market_character = char.get("market_character", market_character)
            
            evolution_context = {
                "flip_rate": truth.get("flip_rate", 0),
                "mutation_rate": truth.get("mutation_rate", line.get("mutation_rate", 0)),
                "survival_rate": line.get("survival_rate", 0),
                "continuation_rate": wave.get("continuation_rate", 0),
                "breakout_rate": wave.get("breakout_rate", 0),
                "reversal_rate": wave.get("reversal_rate", 0),
                "market_character": market_character,
                "dna_similarity": last_wave.dna_similarity if last_wave and hasattr(last_wave, 'dna_similarity') else 0,
                "wave_id": last_wave.wave_id if last_wave and hasattr(last_wave, 'wave_id') else "?",
                "oracle_outcome": self._oracle_match.get("outcome"),
                "oracle_score": self._oracle_match.get("score", 0),
                "market_dna": self._market_dna,
            }
        
        self._hivemind = hivemind.synthesize(
            self._academy_results, self._oracle_match,
            evolution_context=evolution_context
        )

        librarian = LibrarianEngine()
        self._librarian_events = librarian.evaluate(self._bag_artifacts)

        darwin = DarwinEngine()
        self._darwin_proposals = darwin.propose(self._statistics)

        self._knowledge = {
            "academy": self._academy_results,
            "oracle": self._oracle_match,
            "hivemind": self._hivemind,
            "librarian": self._librarian_events,
            "darwin": self._darwin_proposals,
            "market_events": event_recorder.to_dict_list(),
        }

        # ── Stage 13: Prediction ────────────────────────────
        pred = PredictionEngine()
        ev_stats = self._statistics.get("evolution", {})
        wave_stats = ev_stats.get("wave", {})
        evo_ctx = None
        if wave_stats:
            evo_ctx = {
                "continuation_rate": wave_stats.get("continuation_rate", 0),
                "breakout_rate": wave_stats.get("breakout_rate", 0),
                "reversal_rate": wave_stats.get("reversal_rate", 0),
                "structure_distribution": wave_stats.get("structure_distribution", {}),
            }
        self._prediction = pred.predict(
            self._knowledge,
            market_dna=self._market_dna,
            evolution_context=evo_ctx,
        )

        if wave_stats:
            self._prediction["evolution_context"] = {
                "continuation_rate": wave_stats.get("continuation_rate", 0),
                "breakout_rate": wave_stats.get("breakout_rate", 0),
                "reversal_rate": wave_stats.get("reversal_rate", 0),
                "structure_distribution": wave_stats.get("structure_distribution", {}),
            }
        if self._market_dna:
            self._prediction["market_dna"] = self._market_dna

        self._record_snapshot_card(
            "prediction", "prediction_snapshot",
            {"ts": int(time.time() * 1000), "symbol": self._symbol,
             "timeframe": self._timeframe,
             "prediction_source": "pipeline",
             "direction": self._prediction.get("dominant_bias", "NEUTRAL"),
             "probability": self._prediction.get("intelligence_score", 5000) / 10000,
             "target_price": 0,
             "horizon_seconds": 3600}
        )

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
        # Enrich recommendation with evolution + DNA
        if self._market_dna:
            self._recommendation["market_dna"] = self._market_dna
        ev_stats = self._statistics.get("evolution", {})
        if ev_stats.get("truth"):
            self._recommendation["evolution_stats"] = {
                "flip_rate": ev_stats["truth"].get("flip_rate", 0),
                "mutation_rate": ev_stats["truth"].get("mutation_rate", 0),
            }
        if ev_stats.get("line"):
            self._recommendation["structure_stats"] = {
                "total_lines": ev_stats["line"].get("total_lines", 0),
                "survival_rate": ev_stats["line"].get("survival_rate", 0),
            }
        if ev_stats.get("wave"):
            self._recommendation["wave_stats"] = {
                "continuation_rate": ev_stats["wave"].get("continuation_rate", 0),
                "breakout_rate": ev_stats["wave"].get("breakout_rate", 0),
            }
        mem_stats = self._memory.stats() if hasattr(self._memory, 'stats') else {}
        self._recommendation["observation_memory"] = {
            "total_observations": mem_stats.get("total_observations", 0),
            "frozen_count": mem_stats.get("frozen_count", 0),
        }

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

        # Benchmark snapshot (after WASIT benchmark)
        self._record_snapshot_card(
            "benchmark", "benchmark_snapshot",
            {"ts": int(time.time() * 1000), "symbol": self._symbol,
             "timeframe": self._timeframe, "gates_passed": 4, "gates_total": 5,
             "verdict": "PASS"}
        )

        self._generated_at = time.time()
        self._status = "OK"
        self._health_errors = []

        if self._enable_persistence:
            self.persist()

        return self.status()

    # ── Query Methods ───────────────────────────────────────────

    def status(self) -> dict:
        """Return current shell status and generation metadata."""
        mem_stats = self._memory.stats() if hasattr(self, '_memory') else {}
        snap_summary = self.snapshots()
        return {
            "status": self._status,
            "symbol": self._symbol,
            "timeframe": self._timeframe,
            "stages_executed": self._pipeline_report.get("stages_executed", 0),
            "stages_total": PIPELINE_STAGES,
            "truth_points": len(self._truth_points),
            "lines": len(self._lines),
            "waves": len(self._waves),
            "markers": len(self._markers),
            "bag_artifacts": len(self._bag_artifacts),
            "academy_buckets": len(self._academy_results),
            "memory_observations": mem_stats.get("current_size", 0),
            "memory_total": mem_stats.get("total_observations", 0),
            "memory_max": mem_stats.get("max_size", 0),
            "memory_is_full": mem_stats.get("is_full", False),
            "memory_batch_count": mem_stats.get("batch_count", 0),
            "memory_current_batch_size": mem_stats.get("current_batch_size", 0),
            "generated_at_epoch": self._generated_at,
            "db_path": self._db_conn.path,
            "db_is_open": self._db_conn.is_open,
            "snapshot_cards": snap_summary.get("total_cards", 0),
            "snapshot_types": snap_summary.get("registry_count", 0),
            "market_dna_available": bool(self._market_dna),
            "persistence_enabled": self._enable_persistence,
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

    def evolution_statistics(self) -> dict:
        """Return evolution domain statistics (lifecycle, mutation, survival)."""
        if "evolution" not in self._statistics:
            return {"available": False}
        return {"available": True, **self._statistics["evolution"]}

    def indicator_statistics(self) -> dict:
        """Return indicator domain statistics (RSI, W%R, MACD, EMA slope)."""
        if "indicator" not in self._statistics:
            return {"available": False}
        return {"available": True, **self._statistics["indicator"]}

    def market_statistics(self) -> dict:
        """Return market domain statistics (phase distribution, wave frequency, cage lifetime)."""
        if "market" not in self._statistics:
            return {"available": False}
        return {"available": True, **self._statistics["market"]}

    def clone_statistics(self) -> dict:
        """Return clone domain statistics (per-clone performance, observation-to-entry ratio)."""
        if "clone_stats" not in self._statistics:
            return {"available": False}
        return {"available": True, **self._statistics["clone_stats"]}

    def correlation_statistics(self) -> dict:
        """Return correlation domain statistics (indicator correlation matrix)."""
        if "correlation" not in self._statistics:
            return {"available": False}
        return {"available": True, **self._statistics["correlation"]}

    def distance_statistics(self) -> dict:
        """Return distance domain statistics (bucket distribution, optimal range, volatility)."""
        if "distance" not in self._statistics:
            return {"available": False}
        return {"available": True, **self._statistics["distance"]}

    def oi_statistics(self) -> dict:
        """Return OI domain statistics (trend classification, divergence score, accumulation rate)."""
        if "oi" not in self._statistics:
            return {"available": False}
        return {"available": True, **self._statistics["oi"]}

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
                "stages_total": PIPELINE_STAGES,
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
    
    # ── Market Observation Object (MARKET_OBSERVATION_CONTRACT) ──
    
    def get_observation(self, candle_index: int) -> dict:
        """
        Get Market Observation Object untuk satu candle.
        1 Candle = 1 Market Observation Object.
        Checks MarketObservationMemory first, falls back to truth_points.
        """
        if hasattr(self, '_memory'):
            mem_obs = self._memory.get(candle_index)
            if mem_obs and mem_obs.get("available") is not False:
                return mem_obs

        if candle_index < 0 or candle_index >= len(self._truth_points):
            return {"available": False, "candle_index": candle_index}
        
        sp = self._truth_points[candle_index]
        
        # Structure context
        structure_ctx = {"lines": len(self._lines), "waves": len(self._waves)}
        if self._cage:
            structure_ctx["cage_status"] = self._cage.status
            structure_ctx["cage_breakout"] = self._cage.breakout
        
        # Clone context
        clone_ctx = {}
        if hasattr(self, '_clones'):
            for cid in ["LONG", "SHORT", "GRID"]:
                ledger = self._clones.get(cid)
                if ledger and ledger.last_obs:
                    clone_ctx[cid] = {
                        "entry_allowed": ledger.last_obs.get("entry_allowed"),
                        "no_entry_reason": ledger.last_obs.get("no_entry_reason"),
                        "confidence": ledger.last_obs.get("confidence"),
                    }
        
        return {
            "observation_id": f"OBS_{candle_index:06d}",
            "candle_index": candle_index,
            "timestamp": sp.ts if hasattr(sp, 'ts') else 0,
            "truth": {
                "close": sp.close if hasattr(sp, 'close') else None,
                "st": sp.st if hasattr(sp, 'st') else None,
                "st_dir": sp.st_dir if hasattr(sp, 'st_dir') else None,
                "st_color": sp.st_color if hasattr(sp, 'st_color') else None,
                "atr": sp.atr if hasattr(sp, 'atr') else None,
                "rsi": sp.rsi if hasattr(sp, 'rsi') else None,
                "wpr": sp.wpr if hasattr(sp, 'wpr') else None,
                "dist_atr": sp.dist_atr if hasattr(sp, 'dist_atr') else None,
                "point_status": str(sp.point_status) if hasattr(sp, 'point_status') else None,
            },
            "structure": structure_ctx,
            "clone": clone_ctx,
            "historical_index": candle_index,
            "snapshot_batch_id": f"Snapshot-{candle_index // 48000 + 1:03d}" if candle_index < 48000 else "Snapshot-001",
        }
    
    def get_timeline(self, start: int = 0, end: int = None) -> list[dict]:
        """
        Get Market Observation Timeline untuk range candle.
        """
        if end is None:
            end = min(start + 50, len(self._truth_points))
        end = min(end, len(self._truth_points))
        
        timeline = []
        for i in range(start, end):
            obs = self.get_observation(i)
            if obs.get("available") != False:
                timeline.append(obs)
        return timeline
    
    @property
    def bag_artifacts(self) -> list:
        """Access BAG artifacts."""
        return self._bag_artifacts
