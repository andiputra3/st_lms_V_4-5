"""
=====================================================
MODULE:     prediction_engine.py
PURPOSE:    Prediction — Market Possibility.
            Empirical + similarity-based. NO MODEL.
            Output: "82% Breakout", "67% Continuation".
            BUKAN: "BUY BTC", "SELL ETH".
OWNER:      PHASE-12 PREDICTION LAYER
=====================================================
"""


class PredictionEngine:
    """Market Possibility — empirical probability, not trading signal."""
    
    def predict(self, knowledge: dict, market_dna: dict = None,
                evolution_context: dict = None) -> dict:
        """
        Generate Market Possibility from Knowledge.

        Returns:
            Dict dengan possibilities, supporting factors, OI context.
        """
        hivemind = knowledge.get("hivemind", {})
        academy = knowledge.get("academy", [])
        oracle = knowledge.get("oracle", {})

        score = hivemind.get("intelligence_score", 5000)
        bias = hivemind.get("dominant_bias", "NEUTRAL")

        dna_adj = 0
        if market_dna:
            regime = market_dna.get("regime", "")
            if regime == "TRENDING":
                dna_adj = 300
            elif regime == "RANGING":
                dna_adj = -200
            elif regime == "CHOPPY":
                dna_adj = -500
            dominant_wave = market_dna.get("dominant_wave", "")
            if "CONTINUATION" in dominant_wave:
                dna_adj += 200
            elif "REVERSAL" in dominant_wave:
                dna_adj -= 150

        evo_adj = 0
        if evolution_context:
            cont_rate = evolution_context.get("continuation_rate", 0)
            breakout_rate = evolution_context.get("breakout_rate", 0)
            reversal_rate = evolution_context.get("reversal_rate", 0)
            if cont_rate > 50:
                evo_adj += 200
            if breakout_rate > 30:
                evo_adj += 150
            if reversal_rate > 30:
                evo_adj -= 300

        adjusted_score = max(0, min(10000, score + dna_adj + evo_adj))

        possibilities = []

        if bias == "BULLISH":
            possibilities = [
                {"type": "BREAKOUT_UP", "probability": round(adjusted_score / 10000 * 0.85, 2),
                 "confidence": "HIGH" if adjusted_score > 7000 else "MEDIUM"},
                {"type": "CONTINUATION_UP", "probability": round(adjusted_score / 10000 * 0.10, 2),
                 "confidence": "LOW"},
                {"type": "REVERSAL_DOWN", "probability": round((10000 - adjusted_score) / 10000 * 0.05, 2),
                 "confidence": "LOW"},
            ]
        elif bias == "BEARISH":
            possibilities = [
                {"type": "BREAKDOWN_DOWN", "probability": round(adjusted_score / 10000 * 0.85, 2),
                 "confidence": "HIGH" if adjusted_score > 7000 else "MEDIUM"},
                {"type": "CONTINUATION_DOWN", "probability": round(adjusted_score / 10000 * 0.10, 2),
                 "confidence": "LOW"},
                {"type": "REVERSAL_UP", "probability": round((10000 - adjusted_score) / 10000 * 0.05, 2),
                 "confidence": "LOW"},
            ]
        else:
            possibilities = [
                {"type": "RANGE_CONTINUATION", "probability": 0.60, "confidence": "MEDIUM"},
                {"type": "BREAKOUT_UP", "probability": 0.20, "confidence": "LOW"},
                {"type": "BREAKDOWN_DOWN", "probability": 0.20, "confidence": "LOW"},
            ]

        top_academy = academy[0] if academy else {}
        oracle_match = oracle.get("match", False)

        return {
            "possibilities": possibilities,
            "intelligence_score": adjusted_score,
            "dominant_bias": bias,
            "supporting_factors": {
                "knowledge": {
                    "signal": "STRONG" if top_academy.get("win_rate", 0) > 60 else "MODERATE",
                    "detail": f"Top pattern: {top_academy.get('key', 'N/A')} ({top_academy.get('win_rate', 0)}%)",
                },
                "oracle": {
                    "signal": "STRONG" if oracle_match else "NONE",
                    "detail": f"Similarity: {oracle.get('score', 0)}",
                },
            },
            "model_type": "EMPIRICAL",
            "no_model": True,
            "dna_adjustment": dna_adj,
            "evolution_adjustment": evo_adj,
        }
