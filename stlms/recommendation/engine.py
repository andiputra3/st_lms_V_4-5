"""
=====================================================
MODULE:     recommendation_engine.py
PURPOSE:    Recommendation Layer — Market Intelligence Report.
            Gabungan seluruh layer menjadi satu laporan.
            BUKAN sinyal BUY/SELL.
OWNER:      PHASE-15 RECOMMENDATION LAYER
=====================================================
"""


class RecommendationEngine:
    """Market Intelligence Report Package builder."""
    
    def build_report(self, market_pkg: dict, truth_pkg: dict,
                     structure_pkg: dict, knowledge_pkg: dict,
                     prediction_pkg: dict, schema: dict) -> dict:
        """
        Bangun Market Intelligence Report dari seluruh package.
        
        Reference: RECOMMENDATION_LAYER_OUTPUT_CONTRACT.md (20 sections)
        """
        truth_cur = truth_pkg.get("current", {})
        struct_cur = structure_pkg.get("current", {}) if structure_pkg else {}
        
        # Confidence aggregation
        confidences = []
        if truth_pkg.get("valid_points", 0) > 0:
            confidences.append(95)
        if structure_pkg.get("status") == "OK":
            confidences.append(90)
        if knowledge_pkg.get("oracle", {}).get("match"):
            confidences.append(85)
        overall_conf = round(sum(confidences) / len(confidences)) if confidences else 50
        
        return {
            "header": {
                "report_id": f"MIR_{market_pkg.get('symbol', '?')}",
                "symbol": market_pkg.get("symbol"),
                "timeframe": market_pkg.get("timeframe"),
            },
            "current_state": {
                "phase": struct_cur.get("cage_status", "?"),
                "character": knowledge_pkg.get("character", "?"),
            },
            "truth_summary": {
                "supertrend": {
                    "value": truth_cur.get("st"),
                    "direction": "UP" if truth_cur.get("st_dir") == 1 else "DOWN",
                },
                "distance_atr": truth_cur.get("dist_atr"),
                "rsi": truth_cur.get("rsi"),
                "wpr": truth_cur.get("wpr"),
            },
            "structure_summary": struct_cur,
            "knowledge_summary": {
                "academy_top": knowledge_pkg.get("academy", [{}])[0] if knowledge_pkg.get("academy") else {},
                "oracle_match": knowledge_pkg.get("oracle", {}).get("match", False),
                "hivemind_bias": knowledge_pkg.get("hivemind", {}).get("dominant_bias"),
            },
            "prediction_summary": {
                "possibilities": prediction_pkg.get("possibilities", []),
                "model_type": "EMPIRICAL",
            },
            "trading_schema": {
                "market": schema.get("market_schema"),
                "entry": schema.get("entry_schema"),
                "active": schema.get("active_clones", []),
            },
            "action_plan": {
                "prepare": "Monitor market condition",
                "invalidation": "Market phase change",
            },
            "confidence": overall_conf,
            "verdict": {
                "disclaimer": "Market Intelligence Report — NOT a trading signal. NOT financial advice.",
            }
        }
