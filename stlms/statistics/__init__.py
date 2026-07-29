"""
=====================================================
MODULE:     statistics/__init__.py
PURPOSE:    Statistics Layer — aggregate, domain-specific
            statistics across market, indicators,
            distance, clones, OI, and correlations.
OWNER:      STATISTICS LAYER
=====================================================
"""

from .artifact import StatisticsArtifact
from .package import StatisticsPackage
from .validator import StatisticsValidator
from .consumer import StatisticsConsumer
from .domains import (
    MarketStatistics,
    IndicatorStatistics,
    DistanceStatistics,
    CloneStatistics,
    OIStatistics,
    CorrelationStatistics,
)

__all__ = [
    "StatisticsArtifact",
    "StatisticsPackage",
    "StatisticsValidator",
    "StatisticsConsumer",
    "MarketStatistics",
    "IndicatorStatistics",
    "DistanceStatistics",
    "CloneStatistics",
    "OIStatistics",
    "CorrelationStatistics",
]
