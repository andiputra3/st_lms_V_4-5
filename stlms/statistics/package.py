"""
=====================================================
MODULE:     statistics/package.py
PURPOSE:    Statistics Package — builds structured
            StatisticsReport from statistics_snapshot
            cards.
OWNER:      STATISTICS LAYER
=====================================================
"""

from typing import Any
from ..core.utils import Card
from ..foundation.base_package import BasePackage


class StatisticsPackage(BasePackage):
    """
    Build StatisticsReport from statistics_snapshot cards.

    Aggregates multiple statistics snapshots into a
    structured report with cross-domain summaries.
    """

    def __init__(self):
        super().__init__("STATISTICS")

    def build(self, artifacts: list[Card]) -> dict:
        """
        Build structured StatisticsReport from artifacts.

        Returns:
            StatisticsReport dict
        """
        if not artifacts:
            return {
                "layer": self.layer,
                "status": "EMPTY",
                "snapshots": 0,
                "domains": {},
            }

        domains_seen: set[str] = set()
        domain_summaries: dict[str, dict] = {}

        for card in artifacts:
            p = card.payload
            for domain_name, domain_result in p.get("domains", {}).items():
                domains_seen.add(domain_name)
                if domain_name not in domain_summaries:
                    domain_summaries[domain_name] = {
                        "count": 0,
                        "keys": list(domain_result.keys()) if isinstance(domain_result, dict) else [],
                    }
                domain_summaries[domain_name]["count"] += 1

        return {
            "layer": self.layer,
            "symbol": artifacts[0].payload.get("symbol", "?"),
            "clone_id": artifacts[0].payload.get("clone_id", ""),
            "snapshots": len(artifacts),
            "domains": {
                d: {
                    "snapshots": domain_summaries[d]["count"],
                    "metrics": domain_summaries[d]["keys"],
                }
                for d in sorted(domains_seen)
            },
            "status": "OK",
        }

    def summary(self, report: dict) -> str:
        """Human-readable summary of the statistics report."""
        if report.get("status") == "EMPTY":
            return "Statistics Report: No data"

        domains = report.get("domains", {})
        domain_list = ", ".join(domains.keys())
        return (
            f"Statistics Report: {report.get('symbol', '?')} | "
            f"Snapshots: {report.get('snapshots', 0)} | "
            f"Domains: {domain_list}"
        )
