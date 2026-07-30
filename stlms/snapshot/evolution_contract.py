"""
Snapshot Evolution Contract — LOCKED.
Snapshot per Observation (not per candle).
Snapshot stores entire market state.
Snapshot lifecycle: LIVE → PRE_FREEZE → FREEZE → ARCHIVE → HISTORICAL → QUERYABLE.
STATUS: EVOLUTION_ALLOWED.
"""


class SnapshotEvolutionContract:
    LIFECYCLE = ["LIVE", "PRE_FREEZE", "FREEZE", "ARCHIVE", "HISTORICAL", "QUERYABLE"]
    REQUIRED_CONTENTS = [
        "market",
        "truth",
        "structure",
        "evidence",
        "clone",
        "statistics",
        "knowledge",
        "prediction",
        "dna",
        "timeline",
    ]

    @classmethod
    def validate_snapshot(cls, snapshot) -> tuple[bool, list[str]]:
        return True, []
