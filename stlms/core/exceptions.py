"""
ST-LMS v3 — Shared Exceptions
Foundation Core — Phase 1
"""

class STLMSError(Exception):
    """Base exception for all ST-LMS errors."""
    pass

class ValidationError(STLMSError):
    """Raised when data validation fails."""
    pass

class ConstraintError(STLMSError):
    """Raised when SQLite constraint is violated."""
    pass

class WarmupError(STLMSError):
    """Raised when operation is attempted during WARMUP state."""
    pass

class InsufficientDataError(STLMSError):
    """Raised when required data is missing."""
    pass

class ConfigurationError(STLMSError):
    """Raised when configuration is invalid."""
    pass

class BoundedRangeError(ConfigurationError):
    """Raised when value is outside BOUNDED parameter range."""
    pass

class DeterminismError(STLMSError):
    """Raised when determinism check fails."""
    pass

class CardVerificationError(STLMSError):
    """Raised when card checksum verification fails."""
    pass

class PipelineError(STLMSError):
    """Raised when pipeline stage order or type is violated."""
    pass

class WorkerError(STLMSError):
    """Raised when worker communication fails."""
    pass
