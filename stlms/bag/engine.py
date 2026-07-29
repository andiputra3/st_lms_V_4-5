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
