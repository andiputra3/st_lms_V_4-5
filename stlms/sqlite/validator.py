"""
ST-LMS v3 — SQLite Validation Manager
Foundation Core — Phase 1
"""

from .connection import SQLiteConnection
from .manager import SQLiteManager

class SQLiteValidator:
    def __init__(self, connection: SQLiteConnection):
        self._conn = connection
        self._mgr = SQLiteManager(connection)

    def run_all(self) -> list[dict]:
        results = []
        results.append(self._check("Schema tables exist", self._check_tables_exist))
        results.append(self._check("Schema indexes exist", self._check_indexes_exist))
        results.append(self._check("Schema triggers exist", self._check_triggers_exist))
        results.append(self._check("Integrity check", self._check_integrity))
        results.append(self._check("Foreign key check", self._check_fk))
        results.append(self._check("Seed data present", self._check_seed_data))
        return results

    def _check(self, name: str, fn) -> dict:
        try:
            passed, detail = fn()
        except Exception as e:
            passed, detail = False, str(e)
        return {"name": name, "passed": passed, "detail": detail}

    def _check_tables_exist(self) -> tuple[bool, str]:
        count = self._mgr.table_count()
        return (count >= 40, f"{count} tables (expected >= 40)")

    def _check_indexes_exist(self) -> tuple[bool, str]:
        count = self._mgr.index_count()
        return (count >= 9, f"{count} indexes (expected >= 9)")

    def _check_triggers_exist(self) -> tuple[bool, str]:
        count = self._mgr.trigger_count()
        return (count >= 4, f"{count} triggers (expected >= 4)")

    def _check_integrity(self) -> tuple[bool, str]:
        ok, detail = self._mgr.integrity_check()
        return (ok, detail)

    def _check_fk(self) -> tuple[bool, str]:
        violations = self._mgr.foreign_key_check()
        return (len(violations) == 0, f"{len(violations)} FK violations")

    def _check_seed_data(self) -> tuple[bool, str]:
        tf_count = self._mgr.table_row_count("timeframes")
        settings_count = self._mgr.table_row_count("app_settings")
        domains_count = self._mgr.table_row_count("domain_dictionary")
        ok = tf_count >= 9 and settings_count >= 2 and domains_count >= 15
        return (ok, f"timeframes={tf_count}, settings={settings_count}, domains={domains_count}")
