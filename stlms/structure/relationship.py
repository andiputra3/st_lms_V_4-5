"""
Market Relationship Graph — PHASE-06.
Build entity relationship graph.
Truth ↔ Wave, Wave ↔ Cage, Cage ↔ Character, Character ↔ Knowledge.
Market is actually a graph.
STATUS: EVOLUTION_ALLOWED
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Relationship:
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    relationship_type: str  # "produces", "influences", "contains", "depends_on"
    strength: float  # 0.0 to 1.0


class MarketRelationshipGraph:
    def __init__(self):
        self._relationships: list[Relationship] = []

    def add_relationship(self, source_type, source_id, target_type, target_id, rel_type, strength):
        self._relationships.append(Relationship(source_type, source_id, target_type, target_id, rel_type, strength))

    def get_relationships(self, entity_type, entity_id=None):
        result = []
        for r in self._relationships:
            if r.source_type == entity_type or r.target_type == entity_type:
                if entity_id is None or r.source_id == entity_id or r.target_id == entity_id:
                    result.append(r)
        return result

    def get_related_entities(self, entity_type, entity_id, relationship_type=None):
        entities = []
        for r in self._relationships:
            if r.source_type == entity_type and r.source_id == entity_id:
                if relationship_type is None or r.relationship_type == relationship_type:
                    entities.append({"type": r.target_type, "id": r.target_id, "strength": r.strength})
            elif r.target_type == entity_type and r.target_id == entity_id:
                if relationship_type is None or r.relationship_type == relationship_type:
                    entities.append({"type": r.source_type, "id": r.source_id, "strength": r.strength})
        return entities

    def get_graph_summary(self):
        types = {}
        for r in self._relationships:
            types[r.source_type] = types.get(r.source_type, 0) + 1
            types[r.target_type] = types.get(r.target_type, 0) + 1
        return {"total_relationships": len(self._relationships), "entity_types": len(types), "by_type": types}

    def get_strongest_relationships(self, top_n=10):
        sorted_rels = sorted(self._relationships, key=lambda r: r.strength, reverse=True)
        return sorted_rels[:top_n]

    def build_from_pipeline(self, lines, waves, cage, truth_points):
        """Build relationship graph from pipeline data."""
        # Truth → Line
        for i, line in enumerate(lines):
            self.add_relationship("TruthPoint", f"sp_range", "Line", f"line_{i}", "produces", 1.0)

        # Line → Wave
        for i, wave in enumerate(waves):
            for j in range(6):
                self.add_relationship("Line", f"line_{i*6+j}", "Wave", f"wave_{i}", "produces", 0.9)

        # Wave → Cage
        if cage:
            for i, wave in enumerate(waves):
                self.add_relationship("Wave", f"wave_{i}", "Cage", "cage", "influences", 0.7)

        # Cage → MarketCharacter (if available)
        if cage and hasattr(cage, 'status'):
            self.add_relationship("Cage", "cage", "MarketCharacter", "character", "influences", 0.8 if cage.status != "NONE" else 0.3)

        # Character → Knowledge (bidirectional)
        self.add_relationship("MarketCharacter", "character", "Knowledge", "academy", "influences", 0.6)
        self.add_relationship("MarketCharacter", "character", "Knowledge", "hivemind", "influences", 0.7)
        self.add_relationship("Knowledge", "hivemind", "MarketCharacter", "character", "informs", 0.5)

        # Reverse edges
        self.add_relationship("Line", "line_all", "TruthPoint", "sp_all", "contains", 1.0)
        self.add_relationship("Wave", "wave_all", "Line", "line_all", "contains", 0.9)
        self.add_relationship("Cage", "cage", "Wave", "wave_all", "constrains", 0.7)

        return self.get_graph_summary()
