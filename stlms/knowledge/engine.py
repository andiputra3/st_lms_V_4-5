"""
=====================================================
MODULE:     knowledge_engine.py
PURPOSE:    Knowledge Layer — Academy, Oracle, HiveMind,
            CERMIN, Librarian, Darwin.
            Unidirectional, no-ML, card-agnostic.
OWNER:      PHASE-11 KNOWLEDGE LAYER
=====================================================
"""

from ..core.constants import ORACLE_VECTOR_SIZE
from ..core.utils import norm01


class AcademyEngine:
    """Empirical win_rate per bucket. Sample-gated."""
    
    def learn(self, bag_artifacts: list) -> list[dict]:
        results = []
        for bag in bag_artifacts:
            if bag.sample_count >= 30:
                expectancy = sum(m.net for m in bag.patterns if hasattr(m, 'net')) / bag.sample_count if bag.sample_count > 0 else 0
                results.append({
                    "key": bag.bag_key,
                    "sample": bag.sample_count,
                    "win_rate": bag.win_rate,
                    "expectancy": round(expectancy, 3),
                    "confidence": bag.confidence,
                    "maturity": bag.maturity_score,
                    "status": "CUKUP" if bag.sample_count >= 30 else "BELUM_CUKUP",
                })
        return results


class OracleEngine:
    """Euclidean similarity matching. Vector beku."""
    
    def __init__(self):
        self.history: list[dict] = []
    
    def vectorize(self, snap: dict) -> list[float]:
        """Build Oracle vector from snapshot. W%R/MACD NOT in vector."""
        wave_map = {
            "STRONG_ACCUMULATION": 1.0, "STRONG_DISTRIBUTION": 0.92,
            "CONTINUATION_UP": 0.83, "CONTINUATION_DOWN": 0.75,
            "CONFIRMED_RANGE": 0.67, "RANGE_EXPANDING": 0.58,
            "RANGE_COMPRESSING": 0.50, "REVERSAL_UP": 0.42,
            "REVERSAL_DOWN": 0.33, "EXHAUSTION_UP": 0.25,
            "EXHAUSTION_DOWN": 0.17, "SIDEWAY": 0.08, "CHAOS": 0.0,
        }
        cage_map = {"VALID_COMPRESSION": 1.0, "LOOSE_SIDEWAY": 0.66, "NONE": 0.0}
        
        return [
            wave_map.get(snap.get("wave_structure", "CHAOS"), 0.0),
            cage_map.get(snap.get("cage_status", "NONE"), 0.0),
            snap.get("pp", 0.5),
            norm01(snap.get("ema", 5000), 0, 10000),
            norm01(snap.get("oi_score", 0), 0, 10000),
            norm01(snap.get("vd", 5000), 0, 10000),
            norm01(snap.get("mtf_final", 5000), 0, 9000),
            norm01(snap.get("rsi", 50), 0, 100),
            norm01(snap.get("dist_atr", 1.0), 0, 3),
        ]
    
    def match(self, current_vec: list[float]) -> dict:
        """Find best historical match. Euclidean distance."""
        if not self.history:
            return {"match": False, "score": 0}
        
        best = None
        best_dist = float("inf")
        
        for h in self.history:
            dist = sum((a - b) ** 2 for a, b in zip(current_vec, h["vector"])) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best = h
        
        score = max(0, 10000 - best_dist * 1000)
        return {
            "match": score > 7500,
            "score": round(score),
            "outcome": best["outcome"] if best else None,
            "ts": best["ts"] if best else None,
        }
    
    def push(self, vector: list[float], ts: int, outcome: str):
        self.history.append({"vector": vector, "ts": ts, "outcome": outcome})
        if len(self.history) > 600:
            self.history = self.history[-600:]


class HiveMindEngine:
    """Market understanding synthesis. NOT a signal."""
    
    def synthesize(self, academy_results: list[dict], oracle_match: dict,
                   evidence_adj: float = 0, evolution_context: dict = None) -> dict:
        top = academy_results[0] if academy_results else None
        pattern_boost = (top["win_rate"] / 100) * 2000 if top else 0
        oracle_boost = (oracle_match["score"] / 10000) * 2000 if oracle_match["match"] else 0
        
        score = max(0, min(10000, 5000 + pattern_boost + oracle_boost + evidence_adj))
        
        historical_learning = []
        evolution_adj = 0
        
        if evolution_context:
            ctx = evolution_context
            
            flip_rate = ctx.get("flip_rate", 0)
            mutation_rate = ctx.get("mutation_rate", 0)
            survival_rate = ctx.get("survival_rate", 0)
            continuation_rate = ctx.get("continuation_rate", 0)
            breakout_rate = ctx.get("breakout_rate", 0)
            reversal_rate = ctx.get("reversal_rate", 0)
            market_character = ctx.get("market_character", {})
            dna_similarity = ctx.get("dna_similarity", 0)
            wave_id = ctx.get("wave_id", "?")
            oracle_outcome = ctx.get("oracle_outcome")
            oracle_score = ctx.get("oracle_score", 0)
            
            if flip_rate > 30:
                instability = (flip_rate / 100) * 800
                evolution_adj -= instability
                historical_learning.append(
                    f"High flip rate ({flip_rate}%) — structure is unstable, reduce confidence"
                )
            
            if mutation_rate > 20:
                volatility = (mutation_rate / 100) * 600
                evolution_adj -= volatility
                historical_learning.append(
                    f"High mutation rate ({mutation_rate}%) — market is unstable, reduce position size"
                )
            
            if survival_rate > 60:
                stability = (survival_rate / 100) * 600
                evolution_adj += stability
                historical_learning.append(
                    f"High survival rate ({survival_rate}%) — structure is resilient"
                )
            
            if continuation_rate > 50:
                if score > 5000:
                    continuation_boost = (continuation_rate / 100) * 500
                    evolution_adj += continuation_boost
                historical_learning.append(
                    f"Strong continuation pattern ({continuation_rate}%) — trend likely to persist"
                )
            
            if breakout_rate > 30:
                activity = (breakout_rate / 100) * 400
                evolution_adj += activity
                historical_learning.append(
                    f"High breakout rate ({breakout_rate}%) — market is active"
                )
            
            if reversal_rate > 30:
                choppiness = (reversal_rate / 100) * 500
                evolution_adj -= choppiness
                historical_learning.append(
                    f"High reversal rate ({reversal_rate}%) — market is choppy, reduce conviction"
                )
            
            if market_character:
                profile = market_character.get("profile", "")
                regime = market_character.get("regime", "")
                dominant_wave = market_character.get("dominant_wave", "")
                if profile:
                    historical_learning.append(
                        f"Market character: {profile} (regime: {regime}, dominant: {dominant_wave})"
                    )
            
            if dna_similarity > 0:
                pct = round(dna_similarity * 100, 1)
                bias_hint = ""
                if oracle_outcome:
                    bias_hint = f" — historically favored {oracle_outcome}"
                historical_learning.append(
                    f"{pct}% similar to Wave #{wave_id}{bias_hint}"
                )
        
        score = max(0, min(10000, score + evolution_adj))
        bias = "BULLISH" if score > 6500 else ("BEARISH" if score < 3500 else "NEUTRAL")
        
        result = {
            "intelligence_score": round(score),
            "dominant_bias": bias,
            "pattern_boost": round(pattern_boost),
            "oracle_boost": round(oracle_boost),
            "evidence_adj": evidence_adj,
            "evolution_adj": round(evolution_adj),
            "historical_learning": historical_learning,
        }
        
        return result


class LibrarianEngine:
    """Lifecycle management. NEW->OBS->TRUSTED->MATURE/DEAD/DEPRECATED."""
    
    def evaluate(self, bag_artifacts: list) -> list[dict]:
        events = []
        for bag in bag_artifacts:
            n = bag.sample_count
            wr = bag.win_rate or 0
            
            if n < 10:
                status = "NEW"
            elif n >= 50 and wr < 30:
                status = "DEAD"
            elif n >= 30 and wr >= 65:
                status = "MATURE"
            elif n >= 30 and wr >= 55:
                status = "TRUSTED"
            elif n >= 50 and 30 <= wr < 40:
                status = "DEPRECATED"
            else:
                status = "OBSERVATION"
            
            events.append({"key": bag.bag_key, "status": status, "sample": n, "win_rate": wr})
        return events


class DarwinEngine:
    """Parameter proposals. NO auto-execute."""
    
    def propose(self, statistics: dict) -> list[dict]:
        proposals = []
        
        for clone_id, stats in statistics.items():
            if stats.get("sample", 0) < 5:
                continue
            
            if stats.get("expectancy", 0) and stats["expectancy"] < 0:
                proposals.append({
                    "type": "TIGHTEN_ENTRY",
                    "target": clone_id,
                    "param": "ENTRY_OFFSET_BASE_K",
                    "reason": f"Negative expectancy: {stats['expectancy']}",
                })
            
            if stats.get("wrong_rate", 0) > 30:
                proposals.append({
                    "type": "TIGHTEN_WRONG",
                    "target": clone_id,
                    "param": "WRONG_ENTRY_PCT",
                    "reason": f"High wrong rate: {stats['wrong_rate']}%",
                })
        
        return proposals
