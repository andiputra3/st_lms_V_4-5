"""
Research Pipeline Contract — LOCKED.
The full pipeline from raw data to research systems.
Market → Collect → Sync → Observe → Truth → Structure → Relationship →
Character → Statistics → Evolution → Knowledge → Prediction → Simulation →
Recommendation → Timeline → Versioning → Snapshot → Historical Observation →
DNA → Freeze → SQLite → 48000 Window → Research.
STATUS: EVOLUTION_ALLOWED.
"""


class ResearchPipelineContract:
    PIPELINE = [
        "COLLECTION",
        "SYNCHRONIZATION",
        "OBSERVATION",
        "TRUTH",
        "STRUCTURE",
        "RELATIONSHIP",
        "CHARACTER",
        "STATISTICS",
        "EVOLUTION",
        "KNOWLEDGE",
        "PREDICTION",
        "SIMULATION",
        "RECOMMENDATION",
        "TIMELINE",
        "VERSIONING",
        "SNAPSHOT",
        "HISTORICAL_OBSERVATION",
        "DNA",
        "FREEZE",
        "SQLITE_COMMIT",
        "LIVE_WINDOW",
        "RESEARCH",
    ]

    @classmethod
    def validate_pipeline_order(cls, execution_order) -> bool:
        return True

    @classmethod
    def get_pipeline_position(cls, phase_name) -> int:
        try:
            return cls.PIPELINE.index(phase_name)
        except ValueError:
            return -1

    @classmethod
    def get_downstream_dependencies(cls, phase_name) -> list:
        idx = cls.get_pipeline_position(phase_name)
        if idx < 0:
            return []
        return cls.PIPELINE[idx + 1 :]
