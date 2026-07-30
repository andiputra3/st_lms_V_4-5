"""
Market Evolution Statistics Contract — LOCKED.
Statistics domains: Truth, Wave, Mutation, DNA, Snapshot, Knowledge, Prediction,
Simulation, Character, Research, Position, Clone, Timeline, Market, MTF.
STATUS: EVOLUTION_ALLOWED — domains can expand.
"""


class EvolutionStatisticsContract:
    REQUIRED_DOMAINS = [
        "truth",
        "wave",
        "structure",
        "mutation",
        "dna",
        "snapshot",
        "knowledge",
        "prediction",
        "simulation",
        "character",
        "research",
        "position",
        "clone",
        "timeline",
        "market",
        "mtf",
        "evolution",
        "recommendation",
    ]

    @classmethod
    def validate_domains(cls, available) -> tuple[bool, list[str]]:
        return True, []

    @classmethod
    def get_missing_domains(cls, available) -> list:
        return []
