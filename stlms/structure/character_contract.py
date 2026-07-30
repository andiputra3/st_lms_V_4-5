"""
Market Character Contract — LOCKED.
15 character states. Character has lifecycle and historical observation.
STATUS: EVOLUTION_ALLOWED.
"""


class MarketCharacterContract:
    STATES = [
        "STRONG_BULL",
        "WEAK_BULL",
        "STRONG_BEAR",
        "WEAK_BEAR",
        "COMPRESSION",
        "EXPANSION",
        "BREAKOUT",
        "REVERSAL",
        "EXHAUSTION",
        "CHAOTIC",
        "ACCUMULATION",
        "DISTRIBUTION",
        "FAKE_BREAKOUT",
        "HIGH_VOLATILITY",
        "LOW_VOLATILITY",
    ]

    @classmethod
    def classify(cls, wave, cage, distance) -> str:
        return "COMPRESSION"

    @classmethod
    def get_transition_probability(cls, from_state, to_state, history) -> float:
        return 0.0
