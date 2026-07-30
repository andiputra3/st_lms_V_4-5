"""
Historical Observation Contract — LOCKED.
Every observation is preserved forever. Append-only. Immutable.
Market treated as a LIVING entity with observable history.
STATUS: EVOLUTION_ALLOWED.
"""
import hashlib
import json
import uuid


class HistoricalObservationContract:
    REQUIRED_FIELDS = [
        "observation_id",
        "candle_index",
        "timestamp",
        "truth",
        "structure",
        "evidence",
        "clone",
        "statistics",
        "knowledge",
        "prediction",
        "dna",
        "lifecycle",
        "version",
        "mutation",
    ]

    @classmethod
    def validate_observation(cls, obs: dict) -> tuple[bool, list[str]]:
        missing = [f for f in cls.REQUIRED_FIELDS if f not in obs]
        return len(missing) == 0, missing

    @classmethod
    def is_immutable(cls, obs: dict) -> bool:
        if "observation_id" not in obs:
            return False
        if "hash" not in obs:
            return False
        payload = {k: v for k, v in obs.items() if k != "hash"}
        computed = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()
        return computed == obs["hash"]

    @classmethod
    def get_observation_lineage(cls, obs: dict) -> list:
        lineage = []
        if "version" in obs and isinstance(obs["version"], dict):
            lineage = obs["version"].get("history", [])
        if "mutation" in obs and isinstance(obs["mutation"], dict):
            lineage.extend(obs["mutation"].get("ancestors", []))
        return lineage

    @classmethod
    def create_observation(cls, candle_index: int, timestamp, **fields) -> dict:
        obs = {
            "observation_id": str(uuid.uuid4()),
            "candle_index": candle_index,
            "timestamp": timestamp,
            "truth": fields.get("truth", {}),
            "structure": fields.get("structure", {}),
            "evidence": fields.get("evidence", {}),
            "clone": fields.get("clone", {}),
            "statistics": fields.get("statistics", {}),
            "knowledge": fields.get("knowledge", {}),
            "prediction": fields.get("prediction", {}),
            "dna": fields.get("dna", {}),
            "lifecycle": fields.get("lifecycle", "NEW"),
            "version": fields.get("version", {"number": 1, "history": []}),
            "mutation": fields.get("mutation", {"count": 0, "ancestors": []}),
        }
        payload = {k: v for k, v in obs.items()}
        obs["hash"] = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()
        return obs
