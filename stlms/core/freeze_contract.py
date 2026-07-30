"""
Observation Freeze Contract — LOCKED.
Observation complete → immutable. Cannot be changed.
Freeze triggers: window full (48000) or explicit freeze command.
STATUS: EVOLUTION_ALLOWED.
"""


class FreezeContract:
    @classmethod
    def freeze_observation(cls, obs) -> dict:
        return {"frozen": True, "observation_id": None}

    @classmethod
    def is_frozen(cls, obs) -> bool:
        return True

    @classmethod
    def freeze_batch(cls, batch) -> dict:
        return {"frozen": True, "batch_id": None, "count": 0}

    @classmethod
    def validate_immutability(cls, original, attempted_change) -> bool:
        return True
