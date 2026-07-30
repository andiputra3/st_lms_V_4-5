"""
Market Relationship Contract — LOCKED.
Market is a GRAPH. Entities have relationships.
Truth → Line → Wave → Cage → Character → Knowledge → Prediction → Simulation → Recommendation.
STATUS: EVOLUTION_ALLOWED.
"""


class MarketRelationshipContract:
    RELATIONSHIP_CHAIN = [
        "TruthPoint",
        "Line",
        "Wave",
        "Cage",
        "MarketCharacter",
        "Knowledge",
        "Prediction",
        "Simulation",
        "Recommendation",
    ]

    RELATIONSHIP_TYPES = [
        "produces",
        "contains",
        "influences",
        "informs",
        "constrains",
        "depends_on",
    ]

    @classmethod
    def validate_chain_complete(cls, graph) -> bool:
        if not isinstance(graph, dict):
            return False
        for entity_type in cls.RELATIONSHIP_CHAIN:
            if entity_type not in graph:
                return False
        return True

    @classmethod
    def get_missing_relationships(cls, graph) -> list:
        if not isinstance(graph, dict):
            return list(cls.RELATIONSHIP_CHAIN)
        return [et for et in cls.RELATIONSHIP_CHAIN if et not in graph]

    @classmethod
    def get_relationship_strength_threshold(cls, rel_type) -> float:
        thresholds = {
            "produces": 0.8,
            "contains": 0.7,
            "influences": 0.5,
            "informs": 0.6,
            "constrains": 0.4,
            "depends_on": 0.3,
        }
        return thresholds.get(rel_type, 0.5)
