"""
=====================================================
MODULE:     statistics/domains/evolution_stats.py
PURPOSE:    Market Evolution Statistics
OWNER:      STATISTICS LAYER (Stage 12)
ARCHITECTURE: Market Observation Contract
=====================================================
"""

from typing import Optional


class EvolutionStatistics:
    """
    Market Evolution Statistics — metrics tentang
    bagaimana market berubah seiring waktu.
    
    BUKAN trading statistics. Ini adalah statistics
    tentang lifecycle, mutation, survival, dan evolution.
    """
    
    def compute(self, truth_points: list,
                lines: list = None,
                waves: list = None,
                cages: list = None) -> dict:
        """
        Compute evolution statistics dari data observasi.
        
        Args:
            truth_points: list of TruthPoint
            lines: list of Line
            waves: list of Wave
            cages: list of Cage
        
        Returns:
            dict dengan evolution metrics
        """
        result = {
            "truth": self._truth_stats(truth_points),
            "line": self._line_stats(lines or []),
            "wave": self._wave_stats(waves or []),
            "cage": self._cage_stats(cages or []),
        }
        return result
    
    def _truth_stats(self, points: list) -> dict:
        if not points:
            return {"total": 0}
        
        total = len(points)
        valid = sum(1 for p in points if hasattr(p, 'point_status') and str(p.point_status) in ('VALID', 'PointStatus.VALID'))
        flips = sum(1 for p in points if hasattr(p, 'flip') and p.flip)
        mutations = sum(1 for p in points if hasattr(p, 'mutation_count') and p.mutation_count > 0)
        
        return {
            "total_sp": total,
            "valid_sp": valid,
            "warmup_sp": total - valid,
            "flip_count": flips,
            "flip_rate": round(flips / total * 100, 1) if total > 0 else 0,
            "mutation_count": mutations,
            "mutation_rate": round(mutations / total * 100, 1) if total > 0 else 0,
        }
    
    def _line_stats(self, lines: list) -> dict:
        if not lines:
            return {"total": 0}
        
        total = len(lines)
        supports = sum(1 for L in lines if hasattr(L, 'role') and L.role == "SUPPORT")
        resistances = total - supports
        
        members = [L.members for L in lines if hasattr(L, 'members')]
        flips = [L.flip_count for L in lines if hasattr(L, 'flip_count')]
        mutations = [getattr(L, 'mutation_count', 0) for L in lines]
        
        avg_members = sum(members) / len(members) if members else 0
        avg_flips = sum(flips) / len(flips) if flips else 0
        avg_mutations = sum(mutations) / len(mutations) if mutations else 0
        
        # Survival rate: lines with >= 10 members
        survived = sum(1 for m in members if m >= 10)
        
        return {
            "total_lines": total,
            "supports": supports,
            "resistances": resistances,
            "avg_members": round(avg_members, 1),
            "avg_flips": round(avg_flips, 1),
            "flip_rate": round(sum(flips) / total, 1) if total > 0 else 0,
            "avg_mutations": round(avg_mutations, 1),
            "mutation_rate": round(sum(mutations) / total * 100, 1) if total > 0 else 0,
            "survival_rate": round(survived / total * 100, 1) if total > 0 else 0,
        }
    
    def _wave_stats(self, waves: list) -> dict:
        if not waves:
            return {"total": 0}
        
        total = len(waves)
        closed = sum(1 for w in waves if hasattr(w, 'status') and w.status == "CLOSED_WAVE")
        
        structures = {}
        for w in waves:
            s = getattr(w, 'structure', 'UNKNOWN')
            structures[s] = structures.get(s, 0) + 1
        
        continuation = structures.get("CONTINUATION_UP", 0) + structures.get("CONTINUATION_DOWN", 0)
        breakout = structures.get("STRONG_ACCUMULATION", 0) + structures.get("STRONG_DISTRIBUTION", 0)
        reversal = structures.get("REVERSAL_UP", 0) + structures.get("REVERSAL_DOWN", 0)
        
        return {
            "total_waves": total,
            "closed_waves": closed,
            "pending_waves": total - closed,
            "structure_distribution": structures,
            "continuation_rate": round(continuation / total * 100, 1) if total > 0 else 0,
            "breakout_rate": round(breakout / total * 100, 1) if total > 0 else 0,
            "reversal_rate": round(reversal / total * 100, 1) if total > 0 else 0,
        }
    
    def _cage_stats(self, cages: list) -> dict:
        if not cages:
            return {"total": 0}
        
        total = len(cages)
        statuses = {}
        breakouts = {}
        
        for c in cages:
            s = getattr(c, 'status', 'NONE')
            statuses[s] = statuses.get(s, 0) + 1
            b = getattr(c, 'breakout', 'NONE')
            breakouts[b] = breakouts.get(b, 0) + 1
        
        compression_count = statuses.get("VALID_COMPRESSION", 0) + statuses.get("LOOSE_SIDEWAY", 0)
        
        return {
            "total_cages": total,
            "status_distribution": statuses,
            "breakout_distribution": breakouts,
            "compression_frequency": round(compression_count / total * 100, 1) if total > 0 else 0,
        }
