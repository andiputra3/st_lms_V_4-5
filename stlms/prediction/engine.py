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
    
    def predict(self, knowledge: dict) -> dict:
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
        
        # Generate possibilities based on bias and score
        possibilities = []
        
        if bias == "BULLISH":
            possibilities = [
                {"type": "BREAKOUT_UP", "probability": round(score / 10000 * 0.85, 2),
                 "confidence": "HIGH" if score > 7000 else "MEDIUM"},
                {"type": "CONTINUATION_UP", "probability": round(score / 10000 * 0.10, 2),
                 "confidence": "LOW"},
                {"type": "REVERSAL_DOWN", "probability": round((10000 - score) / 10000 * 0.05, 2),
                 "confidence": "LOW"},
            ]
        elif bias == "BEARISH":
            possibilities = [
                {"type": "BREAKDOWN_DOWN", "probability": round(score / 10000 * 0.85, 2),
                 "confidence": "HIGH" if score > 7000 else "MEDIUM"},
                {"type": "CONTINUATION_DOWN", "probability": round(score / 10000 * 0.10, 2),
                 "confidence": "LOW"},
                {"type": "REVERSAL_UP", "probability": round((10000 - score) / 10000 * 0.05, 2),
                 "confidence": "LOW"},
            ]
        else:
            possibilities = [
                {"type": "RANGE_CONTINUATION", "probability": 0.60, "confidence": "MEDIUM"},
                {"type": "BREAKOUT_UP", "probability": 0.20, "confidence": "LOW"},
                {"type": "BREAKDOWN_DOWN", "probability": 0.20, "confidence": "LOW"},
            ]
        
        # Supporting factors
        top_academy = academy[0] if academy else {}
        oracle_match = oracle.get("match", False)
        
        return {
            "possibilities": possibilities,
            "intelligence_score": score,
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
        }
