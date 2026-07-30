"""
Market Research Dashboard Contract — LOCKED.
Dashboard shows: Truth, Wave, Mutation, Timeline, DNA, Knowledge, Statistics, Simulation, Prediction, Snapshot, Historical Observation.
STATUS: EVOLUTION_ALLOWED.
"""


class ResearchDashboardContract:
    REQUIRED_VIEWS = [
        "truth",
        "structure",
        "wave",
        "mutation",
        "timeline",
        "dna",
        "knowledge",
        "statistics",
        "simulation",
        "prediction",
        "snapshot",
        "historical_observation",
        "evolution",
        "lifecycle",
        "pipeline",
        "health",
    ]

    @classmethod
    def validate_views(cls, available_views) -> tuple[bool, list[str]]:
        if not isinstance(available_views, (list, set, dict)):
            return False, list(cls.REQUIRED_VIEWS)
        views = set(available_views)
        missing = [v for v in cls.REQUIRED_VIEWS if v not in views]
        return len(missing) == 0, missing

    @classmethod
    def get_missing_views(cls, available_views) -> list:
        _, missing = cls.validate_views(available_views)
        return missing
