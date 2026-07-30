"""
Market Character Layer — PHASE-07.
Classify what the market is doing RIGHT NOW.
STATUS: EVOLUTION_ALLOWED
"""
from enum import Enum


class MarketCharacterState(Enum):
    STRONG_BULL = "STRONG_BULL"
    WEAK_BULL = "WEAK_BULL"
    STRONG_BEAR = "STRONG_BEAR"
    WEAK_BEAR = "WEAK_BEAR"
    COMPRESSION = "COMPRESSION"
    EXPANSION = "EXPANSION"
    BREAKOUT = "BREAKOUT"
    REVERSAL = "REVERSAL"
    EXHAUSTION = "EXHAUSTION"
    CHAOTIC = "CHAOTIC"
    ACCUMULATION = "ACCUMULATION"
    DISTRIBUTION = "DISTRIBUTION"
    FAKE_BREAKOUT = "FAKE_BREAKOUT"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"


class MarketCharacterEngine:
    def __init__(self):
        self._history: list[dict] = []

    def classify(self, wave, cage, distance_metrics, truth_points) -> MarketCharacterState:
        """Classify current market character based on structure data."""
        if cage is None:
            return MarketCharacterState.CHAOTIC

        cage_status = getattr(cage, 'status', 'NONE')
        breakout = getattr(cage, 'breakout', 'NONE')

        wave_structure = getattr(wave, 'structure', 'CHAOS') if wave else 'CHAOS'
        st_dir = truth_points[-1].st_dir if truth_points else 0

        # Breakout detection
        if breakout in ('IMMINENT_UP', 'SQUEEZE') and cage_status == 'VALID_COMPRESSION':
            return MarketCharacterState.BREAKOUT
        if breakout == 'IMMINENT_DOWN' and cage_status == 'VALID_COMPRESSION':
            return MarketCharacterState.BREAKOUT

        # Compression
        if cage_status == 'VALID_COMPRESSION':
            return MarketCharacterState.COMPRESSION

        # Expansion
        if cage_status == 'LOOSE_SIDEWAY':
            return MarketCharacterState.EXPANSION

        # Bull/Bear based on wave + st_dir
        if wave_structure in ('STRONG_ACCUMULATION', 'CONTINUATION_UP'):
            return MarketCharacterState.STRONG_BULL
        if wave_structure in ('STRONG_DISTRIBUTION', 'CONTINUATION_DOWN'):
            return MarketCharacterState.STRONG_BEAR
        if wave_structure in ('REVERSAL_UP',):
            return MarketCharacterState.REVERSAL
        if wave_structure in ('REVERSAL_DOWN',):
            return MarketCharacterState.REVERSAL
        if wave_structure in ('EXHAUSTION_UP', 'EXHAUSTION_DOWN'):
            return MarketCharacterState.EXHAUSTION

        if st_dir == 1:
            return MarketCharacterState.WEAK_BULL
        elif st_dir == -1:
            return MarketCharacterState.WEAK_BEAR

        return MarketCharacterState.CHAOTIC

    def get_character_profile(self, state=None):
        if state is None:
            return {"state": "UNKNOWN", "profile": {}}
        return {
            "state": state.value,
            "is_trending": state in (MarketCharacterState.STRONG_BULL, MarketCharacterState.STRONG_BEAR, MarketCharacterState.WEAK_BULL, MarketCharacterState.WEAK_BEAR),
            "is_ranging": state in (MarketCharacterState.COMPRESSION, MarketCharacterState.EXPANSION),
            "is_volatile": state in (MarketCharacterState.BREAKOUT, MarketCharacterState.REVERSAL, MarketCharacterState.CHAOTIC),
            "is_accumulating": state == MarketCharacterState.ACCUMULATION,
            "is_distributing": state == MarketCharacterState.DISTRIBUTION,
        }

    def record_character(self, state, candle_index):
        self._history.append({"candle_index": candle_index, "state": state.value})

    def get_character_history(self, window=48000):
        return self._history[-window:]

    def get_dominant_character(self, window=48000):
        recent = self._history[-window:]
        if not recent:
            return MarketCharacterState.CHAOTIC
        counts = {}
        for entry in recent:
            s = entry["state"]
            counts[s] = counts.get(s, 0) + 1
        dominant = max(counts, key=counts.get)
        return MarketCharacterState(dominant)

    def get_character_stability(self, window=100):
        recent = self._history[-window:]
        if len(recent) < 2:
            return 1.0
        changes = sum(1 for i in range(1, len(recent)) if recent[i]["state"] != recent[i-1]["state"])
        return 1.0 - (changes / (len(recent) - 1))
