"""
=====================================================
MODULE:     distance_validator.py
PURPOSE:    Distance Validator — NULL checks, bucket
            classification, trend consistency.
OWNER:      PHASE-05 DISTANCE LAYER
=====================================================
"""

from ..core.utils import Card
from ..core.types import ValidationResult
from ..foundation.base_validator import BaseValidator

VALID_BUCKETS = {"OPTIMAL", "NEAR", "EXTENDED", "FAR", "WARMUP"}
VALID_TRENDS = {"STABLE", "EXPANDING", "CONTRACTING", None}


class DistanceValidator(BaseValidator):

    def __init__(self):
        super().__init__("DISTANCE")

    def validate(self, artifact) -> list[ValidationResult]:
        p = artifact.payload if hasattr(artifact, 'payload') else artifact
        results = []

        dist = p.get("dist")
        dist_atr = p.get("dist_atr")
        bucket = p.get("bucket")
        trend = p.get("trend")
        dist_ceiling = p.get("dist_ceiling")
        dist_floor = p.get("dist_floor")

        results.append(ValidationResult("dist_not_null", dist is not None,
            "dist is present" if dist is not None else "dist is NULL"))
        results.append(ValidationResult("dist_atr_not_null", dist_atr is not None,
            "dist_atr is present" if dist_atr is not None else "dist_atr is NULL"))

        results.append(ValidationResult("dist_non_negative",
            dist is not None and dist >= 0,
            f"dist={dist}" if dist is not None and dist >= 0 else f"Invalid dist={dist}"))

        results.append(ValidationResult("dist_atr_non_negative",
            dist_atr is not None and dist_atr >= 0,
            f"dist_atr={dist_atr}" if dist_atr is not None and dist_atr >= 0 else f"Invalid dist_atr={dist_atr}"))

        results.append(ValidationResult("bucket_valid",
            bucket in VALID_BUCKETS,
            f"bucket={bucket}" if bucket in VALID_BUCKETS else f"Invalid bucket={bucket}"))

        results.append(ValidationResult("trend_valid",
            trend in VALID_TRENDS,
            f"trend={trend}" if trend in VALID_TRENDS else f"Invalid trend={trend}"))

        if trend == "CONTRACTING":
            results.append(ValidationResult("ceiling_null_on_contracting",
                dist_ceiling is None,
                f"dist_ceiling={'NULL' if dist_ceiling is None else dist_ceiling}"))
        if trend == "EXPANDING":
            results.append(ValidationResult("floor_null_on_expanding",
                dist_floor is None,
                f"dist_floor={'NULL' if dist_floor is None else dist_floor}"))

        if bucket == "WARMUP":
            results.append(ValidationResult("warmup_bucket_no_metrics",
                p.get("sdv") is None and p.get("p90") is None,
                "WARMUP bucket has no sdv/p90"))

        return results
