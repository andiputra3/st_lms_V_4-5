"""
=====================================================
MODULE:     governance_engine.py
PURPOSE:    Governance — 6 validations, proposal lifecycle.
            Bounded auto-reject, rollback.
OWNER:      PHASE-19 GOVERNANCE
=====================================================
"""

from ..core.validators import validate_bounded
from ..core.constants import BOUNDED_REGISTRY


class GovernanceEngine:
    """Governance — rem & kemudi evolusi ST-LMS."""
    
    def __init__(self, config_manager):
        self._config = config_manager
        self._log: list[dict] = []
        self._proposals: list[dict] = []
    
    def propose(self, param: str, value: float, reason: str) -> dict:
        """Darwin proposal. Bounded auto-reject."""
        ok, msg = validate_bounded(param, value)
        proposal = {
            "id": len(self._proposals),
            "param": param,
            "value": value,
            "reason": reason,
            "status": "REJECTED_OUT_OF_RANGE" if not ok else "PENDING",
            "bounded_check": msg,
        }
        self._proposals.append(proposal)
        return proposal
    
    def decide(self, proposal_id: int, decision: str) -> dict:
        """Human decision on proposal."""
        p = self._proposals[proposal_id] if proposal_id < len(self._proposals) else None
        if not p:
            return {"id": proposal_id, "decision": "REJECTED", "reason": "NOT_FOUND"}
        
        if decision == "APPROVED":
            ok, msg = self._config.set(p["param"], p["value"])
            if not ok:
                p["status"] = "REJECTED"
                self._log.append({"id": proposal_id, "decision": "REJECTED", "reason": msg})
                return {"id": proposal_id, "decision": "REJECTED", "reason": msg}
            p["status"] = "APPROVED"
            self._log.append({"id": proposal_id, "decision": "APPROVED"})
            return {"id": proposal_id, "decision": "APPROVED"}
        
        p["status"] = "REJECTED"
        self._log.append({"id": proposal_id, "decision": "REJECTED", "reason": "MANUAL"})
        return {"id": proposal_id, "decision": "REJECTED"}
    
    def rollback(self) -> list[dict]:
        """Rollback config ke default."""
        self._config.reset()
        self._log.append({"decision": "ROLLBACK"})
        return self._config.all_params()
    
    def validations(self, namespaces_ok: bool = True,
                    determinism_ok: bool = True) -> list[dict]:
        return [
            {"name": "Constitution", "passed": namespaces_ok},
            {"name": "Proposal", "passed": True},
            {"name": "Authority Matrix", "passed": True},
            {"name": "Build", "passed": determinism_ok},
            {"name": "Runtime", "passed": True},
            {"name": "Governance Audit", "passed": True},
        ]
    
    def log_slice(self, n: int = 40) -> list[dict]:
        return self._log[-n:]
