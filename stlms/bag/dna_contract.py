"""
Market DNA Contract — LOCKED.
Market DNA = compressed fingerprint from all observations.
Contains: Wave distribution, Cage distribution, avg metrics, character, evolution trend, MTF summary.
STATUS: EVOLUTION_ALLOWED.
"""


class MarketDNAContract:
    REQUIRED_COMPONENTS = [
        "wave_distribution",
        "cage_distribution",
        "avg_dist_atr",
        "avg_atr",
        "avg_rsi",
        "dominant_character",
        "evolution_trend",
        "mtf_summary",
        "total_observations",
    ]

    @classmethod
    def validate_dna(cls, dna_profile) -> tuple[bool, list[str]]:
        if not isinstance(dna_profile, dict):
            return False, list(cls.REQUIRED_COMPONENTS)
        missing = [c for c in cls.REQUIRED_COMPONENTS if c not in dna_profile]
        return len(missing) == 0, missing

    @classmethod
    def compare_dna(cls, dna1, dna2) -> float:
        if not isinstance(dna1, dict) or not isinstance(dna2, dict):
            return 0.0
        common_keys = set(dna1.keys()) & set(dna2.keys())
        if not common_keys:
            return 0.0
        matches = 0
        for key in common_keys:
            if dna1.get(key) == dna2.get(key):
                matches += 1
        return matches / len(common_keys) if common_keys else 0.0

    @classmethod
    def get_dna_fingerprint(cls, dna_profile) -> str:
        if not isinstance(dna_profile, dict):
            return ""
        components = []
        for key in cls.REQUIRED_COMPONENTS:
            val = dna_profile.get(key, "?")
            components.append(f"{key}={val}")
        return "|".join(components)
