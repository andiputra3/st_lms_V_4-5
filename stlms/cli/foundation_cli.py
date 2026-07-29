"""
ST-LMS v3 — Foundation CLI
Foundation Core — Phase 1

Lightweight command-line interface for foundation status and validation.
"""

import sys
import os
import time

class FoundationCLI:
    def __init__(self, sqlite_conn=None, config_mgr=None, resource_mgr=None, registry=None):
        self._sqlite = sqlite_conn
        self._config = config_mgr
        self._resource = resource_mgr
        self._registry = registry

    def run(self, args: list[str]) -> None:
        if not args:
            self._help()
            return
        cmd = args[0].lower()
        self._remaining_args = args[1:]
        if cmd == "status":
            self._cmd_status()
        elif cmd == "sqlite":
            self._cmd_sqlite()
        elif cmd == "validate":
            self._cmd_validate()
        elif cmd == "resource":
            self._cmd_resource()
        elif cmd == "benchmark":
            self._cmd_benchmark()
        elif cmd == "config":
            self._cmd_config()
        elif cmd == "mcp":
            self._cmd_mcp()
        elif cmd == "help":
            self._help()
        else:
            print(f"Unknown command: {cmd}")
            self._help()

    def _help(self) -> None:
        print("ST-LMS Foundation CLI")
        print("  status     Foundation status")
        print("  sqlite     SQLite status")
        print("  validate   Foundation validation")
        print("  resource   Resource status")
        print("  benchmark  Benchmark results")
        print("  config     Configuration status")
        print("  mcp        MCP server manager (list/on/off/toggle/tui)")

    def _cmd_status(self) -> None:
        print("=== Foundation Status ===")
        if self._registry:
            s = self._registry.summary()
            print(f"Layers:     {s['layers']}")
            print(f"Components: {s['components']}")
            print(f"Workers:    {s['workers']}")
            print(f"Artifacts:  {s['artifacts']}")
        if self._sqlite:
            print(f"SQLite:     {self._sqlite.path} ({'open' if self._sqlite.is_open else 'closed'})")
        if self._resource:
            r = self._resource.status()
            print(f"Memory:     {r['memory_status']}")
            print(f"CPU:        {r['cpu_seconds']}s")
        print("Status: OK")

    def _cmd_sqlite(self) -> None:
        print("=== SQLite Status ===")
        if not self._sqlite:
            print("SQLite not configured")
            return
        print(f"Path:    {self._sqlite.path}")
        print(f"Open:    {self._sqlite.is_open}")
        if self._sqlite.is_open:
            from ..sqlite.manager import SQLiteManager
            mgr = SQLiteManager(self._sqlite)
            s = mgr.stats
            print(f"Tables:  {s['tables']}")
            print(f"Indexes: {s['indexes']}")
            print(f"Size:    {s['size_bytes']} bytes")

    def _cmd_validate(self) -> None:
        print("=== Foundation Validation ===")
        if self._sqlite and self._sqlite.is_open:
            from ..sqlite.validator import SQLiteValidator
            v = SQLiteValidator(self._sqlite)
            results = v.run_all()
            for r in results:
                status = "PASS" if r["passed"] else "FAIL"
                print(f"  [{status}] {r['name']}: {r['detail']}")

    def _cmd_resource(self) -> None:
        print("=== Resource Status ===")
        if self._resource:
            r = self._resource.status()
            print(f"Memory:  {r['memory_status']}")
            print(f"CPU:     {r['cpu_seconds']}s")
            print(f"Disk:    {r['disk']['used_pct']}% used")

    def _cmd_benchmark(self) -> None:
        print("=== Benchmark Results ===")
        if self._sqlite and self._sqlite.is_open:
            from ..sqlite.benchmark import SQLiteBenchmark
            b = SQLiteBenchmark(self._sqlite)
            results = b.run_all()
            for r in results:
                if r["error"]:
                    print(f"  [FAIL] {r['name']}: {r['error']}")
                else:
                    print(f"  [OK] {r['name']}: {r['elapsed_ms']}ms — {r['result']}")

    def _cmd_config(self) -> None:
        print("=== Configuration Status ===")
        if self._config:
            params = self._config.all_params()
            for p in params:
                print(f"  {p['key']}: {p['current']} (min={p['min']}, max={p['max']})")
        else:
            print("Config not loaded")

    def _cmd_mcp(self) -> None:
        from .mcp_cli import run_cmd
        import sys
        args = self._remaining_args if hasattr(self, '_remaining_args') else []
        run_cmd(args)

def main():
    cli = FoundationCLI()
    cli.run(sys.argv[1:] if len(sys.argv) > 1 else [])

if __name__ == "__main__":
    main()
