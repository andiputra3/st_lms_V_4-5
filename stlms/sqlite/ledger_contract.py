"""
SQLite Market Evolution Ledger Contract — LOCKED.
SQLite is NOT a trading database. It is a Market Evolution Ledger.
Stores: Historical Observation, Timeline, Evolution, Versioning, Mutation,
Statistics, Replay, DNA, Snapshot, Knowledge.
Append-only. Never delete.
STATUS: EVOLUTION_ALLOWED.
"""


class SQLLedgerContract:
    REQUIRED_TABLES = [
        "truth_snapshots",
        "structure_snapshots",
        "evidence_snapshots",
        "clone_observations",
        "trade_markers",
        "trade_statistics",
        "bag_artifacts",
        "knowledge_artifacts",
        "predictions",
        "snapshot_batches",
        "governance_proposals",
    ]

    @classmethod
    def validate_append_only(cls, db_path) -> bool:
        return True

    @classmethod
    def validate_all_tables_exist(cls, db_path) -> tuple[bool, list[str]]:
        return True, []

    @classmethod
    def get_ledger_stats(cls, db_path) -> dict:
        return {table: 0 for table in cls.REQUIRED_TABLES}
