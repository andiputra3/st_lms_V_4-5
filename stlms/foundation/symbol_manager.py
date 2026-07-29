"""
ST-LMS v3 — Symbol Manager
Foundation Core — Phase 1
"""

from ..core.constants import ASSETS

class SymbolManager:
    @staticmethod
    def get(symbol: str) -> dict:
        if symbol not in ASSETS:
            raise KeyError(f"Unknown symbol: {symbol}")
        return ASSETS[symbol]

    @staticmethod
    def exists(symbol: str) -> bool:
        return symbol in ASSETS

    @staticmethod
    def tick_size(symbol: str) -> float:
        return ASSETS[symbol]["tick"]

    @staticmethod
    def precision(symbol: str) -> int:
        return ASSETS[symbol]["prec"]

    @staticmethod
    def base_price(symbol: str) -> float:
        return ASSETS[symbol]["base"]

    @staticmethod
    def all_symbols() -> list[str]:
        return list(ASSETS.keys())
