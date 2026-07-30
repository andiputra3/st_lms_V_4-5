"""
Professional Futures Trader Contract — LOCKED.
Simulates professional futures trader behavior.
Capital, Position, Risk, Leverage, Funding, Portfolio, Competition.
STATUS: EVOLUTION_ALLOWED — 20-30% complete, will evolve.
"""


class ProfessionalTraderContract:
    REQUIRED_CAPABILITIES = [
        "position_sizing",
        "risk_management",
        "capital_allocation",
        "scaling",
        "margin_management",
        "leverage",
        "clone_competition",
        "partial_tp",
        "trailing_stop",
        "breakeven",
        "profit_lock",
        "emergency_exit",
        "funding_management",
        "portfolio_management",
    ]

    @classmethod
    def validate_trader_capabilities(cls, trader) -> tuple[bool, list[str]]:
        if not hasattr(trader, "get_capabilities"):
            missing = list(cls.REQUIRED_CAPABILITIES)
            return False, missing
        available = trader.get_capabilities() if callable(trader.get_capabilities) else []
        missing = [c for c in cls.REQUIRED_CAPABILITIES if c not in available]
        return len(missing) == 0, missing

    @classmethod
    def get_missing_capabilities(cls, trader) -> list:
        _, missing = cls.validate_trader_capabilities(trader)
        return missing

    @classmethod
    def get_capability_status(cls, trader) -> dict:
        if not hasattr(trader, "get_capabilities"):
            return {c: "missing" for c in cls.REQUIRED_CAPABILITIES}
        available = trader.get_capabilities() if callable(trader.get_capabilities) else []
        return {
            c: ("present" if c in available else "missing")
            for c in cls.REQUIRED_CAPABILITIES
        }
