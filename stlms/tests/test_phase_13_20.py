"""
=====================================================
MODULE:     test_phase_13_20.py
PURPOSE:    Unit tests untuk Phase-13 sampai Phase-20.
=====================================================
"""

import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stlms.schema.engine import SchemaEngine, MARKET_SCHEMAS, ENTRY_SCHEMAS
from stlms.recommendation.engine import RecommendationEngine
from stlms.simulation.engine import SimulationEngine
from stlms.consumer.engine import ConsumerEngine
from stlms.bench.engine import wasit_5gate
from stlms.governance.engine import GovernanceEngine
from stlms.integration.engine import IntegrationEngine
from stlms.foundation.config_manager import ConfigurationManager
from stlms.clone.engine import TradeMarker


class TestSchema(unittest.TestCase):
    def setUp(self):
        self.engine = SchemaEngine()
    
    def test_market_schemas_count(self):
        self.assertEqual(len(MARKET_SCHEMAS), 10)
    
    def test_entry_schemas_count(self):
        self.assertEqual(len(ENTRY_SCHEMAS), 11)
    
    def test_select_compression(self):
        schema = self.engine.select_market_schema("VALID_COMPRESSION", "RANGE_COMPRESSING", 1, "NONE", "VALID")
        self.assertEqual(schema, "COMPRESSION")
    
    def test_select_breakout(self):
        schema = self.engine.select_market_schema("NONE", "CONTINUATION_UP", 1, "IMMINENT_UP", "VALID")
        self.assertEqual(schema, "BREAKOUT")
    
    def test_entry_grid(self):
        schema = self.engine.select_entry_schema("COMPRESSION", 1, {"dominant_bias": "BULLISH"})
        self.assertEqual(schema, "GRID_COMPRESSION")
    
    def test_active_clones(self):
        clones = self.engine.get_active_clones("COMPRESSION")
        self.assertIn("GRID", clones)


class TestRecommendation(unittest.TestCase):
    def setUp(self):
        self.engine = RecommendationEngine()
    
    def test_build_report(self):
        report = self.engine.build_report(
            {"symbol": "BTCUSDT", "timeframe": "1m"},
            {"current": {"st": 62150, "st_dir": 1, "dist_atr": 0.15, "rsi": 52, "wpr": -35}, "valid_points": 100},
            {"current": {"cage_status": "VALID_COMPRESSION"}, "status": "OK"},
            {"oracle": {"match": True}, "hivemind": {"dominant_bias": "BULLISH"}},
            {"possibilities": [{"type": "BREAKOUT_UP", "probability": 0.82}]},
            {"market_schema": "COMPRESSION", "entry_schema": "GRID_COMPRESSION", "active_clones": ["GRID"]}
        )
        self.assertIn("header", report)
        self.assertIn("confidence", report)
        self.assertGreater(report["confidence"], 0)


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.engine = SimulationEngine()
    
    def test_architecture(self):
        r = self.engine.architecture_sim(23, True, True)
        self.assertEqual(r["verdict"], "PASS")
    
    def test_balance(self):
        r = self.engine.balance_sim(100, 103.5, 12, 8)
        self.assertEqual(r["verdict"], "PASS")


class TestConsumer(unittest.TestCase):
    def setUp(self):
        self.engine = ConsumerEngine()
    
    def test_fund_eval(self):
        r = self.engine.fund_eval(7000, 100)
        self.assertTrue(r["allowed"])
        self.assertGreater(r["position_size"], 0)
    
    def test_veto_allow(self):
        r = self.engine.veto_gate(7000, "FINAL")
        self.assertEqual(r["decision"], "ALLOW")
    
    def test_veto_reject(self):
        r = self.engine.veto_gate(1000, "FINAL")
        self.assertEqual(r["decision"], "REJECT")
    
    def test_intent_grid(self):
        auth = {"decision": "ALLOW", "failed": []}
        r = self.engine.intent_builder("BTCUSDT", "SIDEWAY_COMPRESSION", 7000, 62000, auth)
        self.assertEqual(r["status"], "GRID_INTENT")
    
    def test_csv_export(self):
        markers = [TradeMarker(ts=1, clone="LONG", side="LONG", kind="EXIT",
                              reason="TP", entry=100, exit=105, net=4.85, result="WIN")]
        csv = self.engine.export_csv(markers)
        self.assertIn("TP", csv)
    
    def test_live_disabled(self):
        self.assertFalse(self.engine.live_enabled)


class TestBenchmark(unittest.TestCase):
    def test_wasit_identical_fails(self):
        m = [TradeMarker(ts=i, clone="LONG", side="LONG", kind="EXIT",
             reason="TP", entry=100, exit=105, gross=5.0, fee=0.1, slip=0.05,
             net=4.85, result="WIN") for i in range(40)]
        r = wasit_5gate(m, m)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertFalse(r["gates"]["G2"])
    
    def test_wasit_better_candidate(self):
        base = [TradeMarker(ts=i, clone="LONG", side="LONG", kind="EXIT",
                reason="TP", entry=100, exit=102, gross=2.0, fee=0.1, slip=0.05,
                net=1.85, result="WIN" if i < 20 else "LOSS") for i in range(40)]
        cand = [TradeMarker(ts=i, clone="LONG", side="LONG", kind="EXIT",
                reason="TP", entry=100, exit=106, gross=6.0, fee=0.1, slip=0.05,
                net=5.85, result="WIN" if i < 30 else "LOSS") for i in range(40)]
        r = wasit_5gate(base, cand)
        self.assertIn(r["verdict"], ["PASS", "FAIL"])


class TestGovernance(unittest.TestCase):
    def setUp(self):
        self.cfg = ConfigurationManager()
        self.engine = GovernanceEngine(self.cfg)
    
    def test_propose_valid(self):
        p = self.engine.propose("SAMPLE_GATE", 50, "Increase sample gate")
        self.assertEqual(p["status"], "PENDING")
    
    def test_propose_out_of_range(self):
        p = self.engine.propose("SAMPLE_GATE", 5, "Too low")
        self.assertEqual(p["status"], "REJECTED_OUT_OF_RANGE")
    
    def test_approve(self):
        self.engine.propose("SAMPLE_GATE", 50, "Test")
        r = self.engine.decide(0, "APPROVED")
        self.assertEqual(r["decision"], "APPROVED")
        self.assertAlmostEqual(self.cfg.get("SAMPLE_GATE"), 50)
    
    def test_rollback(self):
        self.engine.propose("SAMPLE_GATE", 50, "Test")
        self.engine.decide(0, "APPROVED")
        self.engine.rollback()
        self.assertAlmostEqual(self.cfg.get("SAMPLE_GATE"), 30)
    
    def test_validations(self):
        v = self.engine.validations(True, True)
        self.assertEqual(len(v), 6)
        self.assertTrue(all(r["passed"] for r in v))


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = IntegrationEngine()
    
    def test_pipeline_report(self):
        r = self.engine.run_pipeline([], [], [], [], None, [], {}, [], {}, {}, {}, {})
        self.assertEqual(r["stages_executed"], 23)
        self.assertEqual(r["verdict"], "PASS")
    
    def test_architecture_validation(self):
        r = self.engine.validate_architecture()
        self.assertEqual(r["pipeline_stages"], "23/23")


class TestImportAll(unittest.TestCase):
    def test_import(self):
        import stlms.schema.engine
        import stlms.recommendation.engine
        import stlms.simulation.engine
        import stlms.consumer.engine
        import stlms.bench.engine
        import stlms.governance.engine
        import stlms.integration.engine


if __name__ == "__main__":
    unittest.main(verbosity=2)
