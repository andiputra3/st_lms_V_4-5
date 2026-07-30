"""
=====================================================
MODULE:     bag_engine.py
PURPOSE:    BAG — Behavioral Artifact Grouping.
            Group, classify, pattern mine, fingerprint.
OWNER:      PHASE-11 KNOWLEDGE LAYER (BAG sub-layer)
ARCHITECTURE:
            BAG = intermediate antara STATISTICS dan KNOWLEDGE.
            Grouping dipindahkan dari Knowledge ke BAG.
            Knowledge hanya: Learn, Consume, Summarize, Infer, Recommend.
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional
from ..core.types import BagKind, ConsensusLevel, ConflictLevel


@dataclass
class BagArtifact:
    bag_id: str
    bag_kind: BagKind
    bag_key: str
    sample_count: int = 0
    win_count: int = 0
    loss_count: int = 0
    win_rate: Optional[float] = None
    consensus: str = "NONE"
    conflict_level: str = "NONE"
    confidence: float = 0.0
    maturity_score: float = 0.0
    patterns: list[dict] = field(default_factory=list)
    fingerprint: Optional[list[float]] = None


class BAGEngine:
    """
    Behavioral Artifact Grouping Engine.
    
    Operasi:
        Group, Classify, Count, Compare, Summarize, Score, Tag,
        Compress, Fingerprint, Consensus, Conflict, Maturity,
        Behavior Analysis, Sequence Analysis, Pattern Mining.
    """
    
    def group_by_clone_structure(self, markers: list, snapshots: list) -> list[BagArtifact]:
        """
        Group trade markers by (clone, structure, distance_bucket, reason).
        4-dim bucket seperti Academy.
        """
        buckets: dict = {}
        
        for m in markers:
            if m.kind != "EXIT":
                continue
            
            # Find matching snapshot
            snap = next((s for s in snapshots if s.get("ts") == m.ts), None)
            structure = snap.get("wave_structure", "—") if snap else "—"
            dist_atr = snap.get("dist_atr") if snap else None
            
            dist_bucket = "WARMUP"
            if dist_atr is not None:
                if dist_atr <= 0.5:
                    dist_bucket = "OPTIMAL"
                elif dist_atr <= 1.0:
                    dist_bucket = "NEAR"
                elif dist_atr <= 2.0:
                    dist_bucket = "EXTENDED"
                else:
                    dist_bucket = "FAR"
            
            key = f"{m.clone}|{structure}|{dist_bucket}|{m.reason}"
            
            if key not in buckets:
                buckets[key] = {"wins": 0, "losses": 0, "nets": [], "markers": []}
            
            buckets[key]["markers"].append(m)
            if m.result == "WIN":
                buckets[key]["wins"] += 1
            else:
                buckets[key]["losses"] += 1
            if m.net is not None:
                buckets[key]["nets"].append(m.net)
        
        artifacts = []
        for key, data in buckets.items():
            n = data["wins"] + data["losses"]
            wr = data["wins"] / n * 100 if n > 0 else 0
            
            # Consensus
            if wr >= 80:
                consensus = "HIGH"
            elif wr >= 60:
                consensus = "MEDIUM"
            elif wr >= 40:
                consensus = "LOW"
            else:
                consensus = "NONE"
            
            # Conflict
            loss_pct = data["losses"] / n * 100 if n > 0 else 0
            if loss_pct > 30:
                conflict = "HIGH"
            elif loss_pct > 15:
                conflict = "MEDIUM"
            elif loss_pct > 5:
                conflict = "LOW"
            else:
                conflict = "NONE"
            
            # Maturity
            maturity = 0
            if n >= 100:
                maturity += 3000
            if consensus == "HIGH":
                maturity += 3000
            if conflict == "NONE":
                maturity += 2000
            maturity = min(10000, maturity)
            
            artifacts.append(BagArtifact(
                bag_id=f"BAG_{key}",
                bag_kind=BagKind.BEHAVIOR,
                bag_key=key,
                sample_count=n,
                win_count=data["wins"],
                loss_count=data["losses"],
                win_rate=round(wr, 1),
                consensus=consensus,
                conflict_level=conflict,
                confidence=min(10000, wr * 100),
                maturity_score=maturity,
            ))
        
        return artifacts
    
    # ── Market DNA Extraction (MARKET_OBSERVATION_CONTRACT) ──
    
    def extract_dna(self, waves: list, cages: list, truth_points: list) -> dict:
        """
        Extract Market DNA — compressed fingerprint dari observasi.
        
        Returns:
            dict dengan dna_profile
        """
        # Wave structure distribution
        wave_dist = {}
        for w in waves:
            s = getattr(w, 'structure', 'UNKNOWN')
            wave_dist[s] = wave_dist.get(s, 0) + 1
        
        # Cage status distribution
        cage_dist = {}
        for c in cages:
            s = getattr(c, 'status', 'NONE')
            cage_dist[s] = cage_dist.get(s, 0) + 1
        
        # Average metrics
        dist_atrs = [p.dist_atr for p in truth_points if hasattr(p, 'dist_atr') and p.dist_atr]
        atrs = [p.atr for p in truth_points if hasattr(p, 'atr') and p.atr]
        rsis = [p.rsi for p in truth_points if hasattr(p, 'rsi') and p.rsi]
        
        return {
            "dna_profile": {
                "wave_distribution": wave_dist,
                "cage_distribution": cage_dist,
                "avg_dist_atr": round(sum(dist_atrs) / len(dist_atrs), 3) if dist_atrs else 0,
                "avg_atr": round(sum(atrs) / len(atrs), 1) if atrs else 0,
                "avg_rsi": round(sum(rsis) / len(rsis), 1) if rsis else 50,
                "total_observations": len(truth_points),
            }
        }
    
    def analyze_character(self, wave_dist: dict, cage_dist: dict) -> dict:
        """
        Analyze Historical Market Character dari distribution data.
        
        Returns:
            dict dengan market_character profile
        """
        # Determine dominant wave
        dominant_wave = max(wave_dist, key=wave_dist.get) if wave_dist else "UNKNOWN"
        
        # Determine market regime
        compression_pct = (cage_dist.get("VALID_COMPRESSION", 0) + cage_dist.get("LOOSE_SIDEWAY", 0)) / sum(cage_dist.values()) * 100 if cage_dist else 0
        trend_pct = cage_dist.get("NONE", 0) / sum(cage_dist.values()) * 100 if cage_dist else 0
        
        if compression_pct > 60:
            regime = "RANGE_BOUND"
        elif trend_pct > 60:
            regime = "TRENDING"
        else:
            regime = "MIXED"
        
        # Determine profile
        if "CONTINUATION" in dominant_wave or "STRONG" in dominant_wave:
            profile = "TREND_FOLLOWING"
        elif "RANGE" in dominant_wave or "COMPRESSION" in dominant_wave or "SIDEWAY" in dominant_wave:
            profile = "MEAN_REVERSION"
        elif "REVERSAL" in dominant_wave:
            profile = "REVERSAL_HUNTER"
        elif "EXHAUSTION" in dominant_wave:
            profile = "EXHAUSTION_DETECTOR"
        else:
            profile = "ADAPTIVE"
        
        return {
            "market_character": {
                "dominant_wave": dominant_wave,
                "regime": regime,
                "profile": profile,
                "compression_pct": round(compression_pct, 1),
                "trend_pct": round(trend_pct, 1),
            }
        }
