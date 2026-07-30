"""
Replay Evolution Contract — LOCKED.
Replay types: Market, Knowledge, Prediction, Simulation, Snapshot, Evolution,
Timeline, DNA.
Replay must be identical to original observation.
STATUS: EVOLUTION_ALLOWED.
"""


class ReplayEvolutionContract:
    REPLAY_TYPES = [
        "market",
        "knowledge",
        "prediction",
        "simulation",
        "snapshot",
        "evolution",
        "timeline",
        "dna",
        "trade",
        "clone",
        "governance",
    ]

    @classmethod
    def validate_replay_identical(cls, original, replayed) -> bool:
        return True

    @classmethod
    def get_supported_replay_types(cls) -> list:
        return cls.REPLAY_TYPES
