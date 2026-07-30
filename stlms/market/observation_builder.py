"""
Tahap 02 · Market Observation Builder
Tugas: HANYA membuat identitas observasi. TIDAK menghitung indikator.
Output: ObservationIdentity
"""
from dataclasses import dataclass
import uuid
import time


@dataclass
class ObservationIdentity:
    observation_id: str
    session_id: str
    snapshot_id: str
    timeline_id: str
    version_id: str
    symbol: str
    timeframe: str
    candle_index: int


class ObservationBuilder:
    """HANYA membuat ID. Tidak menghitung indikator."""

    def __init__(self, session_id: str | None = None):
        self._session_id = session_id or str(uuid.uuid4())

    def build_identity(self, symbol: str, timeframe: str,
                       candle_index: int) -> ObservationIdentity:
        return ObservationIdentity(
            observation_id=f"obs-{symbol}-{timeframe}-{candle_index:05d}-{uuid.uuid4().hex[:8]}",
            session_id=self._session_id,
            snapshot_id=f"snap-{uuid.uuid4().hex[:12]}",
            timeline_id=f"tl-{uuid.uuid4().hex[:12]}",
            version_id=f"v-{int(time.time())}-{uuid.uuid4().hex[:6]}",
            symbol=symbol,
            timeframe=timeframe,
            candle_index=candle_index,
        )

    def build_batch_identity(self, symbol: str, timeframe: str,
                             count: int) -> list[ObservationIdentity]:
        return [
            self.build_identity(symbol, timeframe, i)
            for i in range(count)
        ]
