"""
Market Research CLI Contract — LOCKED.
CLI is NOT a developer tool. It is a Market Research interface.
Commands: setup, collect, sync, run, replay, dashboard, doctor, statistics, benchmark, export.
STATUS: EVOLUTION_ALLOWED.
"""


class ResearchCLIContract:
    REQUIRED_COMMANDS = [
        "setup",
        "collect",
        "sync",
        "build",
        "run",
        "replay",
        "dashboard",
        "doctor",
        "statistics",
        "benchmark",
        "export",
        "knowledge",
        "prediction",
        "simulation",
        "recommendation",
        "sqlite",
        "snapshot",
        "timeline",
        "health",
        "test",
        "version",
        "help",
    ]

    @classmethod
    def validate_commands(cls, available_commands) -> tuple[bool, list[str]]:
        if not isinstance(available_commands, (list, set, dict)):
            return False, list(cls.REQUIRED_COMMANDS)
        cmds = set(available_commands)
        missing = [c for c in cls.REQUIRED_COMMANDS if c not in cmds]
        return len(missing) == 0, missing

    @classmethod
    def get_missing_commands(cls, available_commands) -> list:
        _, missing = cls.validate_commands(available_commands)
        return missing
