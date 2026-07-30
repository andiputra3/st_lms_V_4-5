"""
Market Evolution Contract — LOCKED.
Market entities have: Lifecycle, Versioning, Mutation, Timeline, Reliability, DNA, Character.
All entities evolve over time.
STATUS: EVOLUTION_ALLOWED.
"""


class MarketEvolutionContract:
    ENTITY_TYPES = [
        "TruthPoint",
        "Line",
        "Wave",
        "Cage",
        "Clone",
        "Knowledge",
        "Prediction",
        "Recommendation",
        "Simulation",
        "Snapshot",
        "DNA",
    ]

    LIFECYCLE_STATES = [
        "NEW",
        "LIVE",
        "UPDATE",
        "MATURE",
        "FREEZE",
        "ARCHIVE",
    ]

    @classmethod
    def validate_entity_has_lifecycle(cls, entity) -> bool:
        if not isinstance(entity, dict):
            return False
        return "lifecycle" in entity and entity["lifecycle"] in cls.LIFECYCLE_STATES

    @classmethod
    def validate_entity_has_version(cls, entity) -> bool:
        if not isinstance(entity, dict):
            return False
        version = entity.get("version")
        if version is None:
            return False
        if isinstance(version, dict):
            return "number" in version
        if isinstance(version, (int, float)):
            return True
        return False

    @classmethod
    def validate_entity_has_mutation_tracking(cls, entity) -> bool:
        if not isinstance(entity, dict):
            return False
        mutation = entity.get("mutation")
        if mutation is None:
            return False
        if isinstance(mutation, dict):
            return "count" in mutation and "ancestors" in mutation
        return False

    @classmethod
    def get_evolution_requirements(cls) -> dict:
        return {
            "entity_types": cls.ENTITY_TYPES,
            "lifecycle_states": cls.LIFECYCLE_STATES,
            "required_fields": ["lifecycle", "version", "mutation"],
            "required_behaviors": [
                "evolve",
                "mutate",
                "version_increment",
                "lifecycle_transition",
            ],
        }
