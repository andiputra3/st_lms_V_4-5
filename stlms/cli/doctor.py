"""
ST-LMS v4 — Doctor Diagnostic System
Comprehensive system diagnostic with health score and recommendations.
"""

import os
import sys
import json
import shutil
import time
import sqlite3
from pathlib import Path


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)


def _banner():
    print()
    print("=" * 55)
    print("   ST-LMS v4 — Doctor")
    print("   Comprehensive System Diagnostic")
    print("=" * 55)
    print()


def _section(title: str):
    print()
    print("-" * 55)
    print(f"  {title}")
    print("-" * 55)


def _ok(msg: str):
    print(f"  [PASS] {msg}")


def _warn(msg: str):
    print(f"  [WARN] {msg}")


def _fail(msg: str):
    print(f"  [FAIL] {msg}")


def _info(msg: str):
    print(f"  [INFO] {msg}")


def check_python() -> dict:
    """Check Python version."""
    ver = sys.version_info
    version_str = f"{ver.major}.{ver.minor}.{ver.micro}"
    ok = ver >= (3, 10)

    if ok:
        _ok(f"Python {version_str} (>= 3.10 required)")
    else:
        _fail(f"Python {version_str} (need 3.10+)")

    return {
        "name": "Python Version",
        "status": "PASS" if ok else "FAIL",
        "detail": f"Python {version_str}",
        "recommendation": None if ok else "Upgrade to Python 3.10 or newer"
    }


def check_sqlite_available() -> dict:
    """Check SQLite availability and version."""
    try:
        ver = sqlite3.sqlite_version
        _ok(f"SQLite {ver} available")
        return {
            "name": "SQLite Available",
            "status": "PASS",
            "detail": f"SQLite {ver}",
            "recommendation": None
        }
    except Exception as e:
        _fail(f"SQLite not available: {e}")
        return {
            "name": "SQLite Available",
            "status": "FAIL",
            "detail": str(e),
            "recommendation": "Install sqlite3 or reinstall Python with sqlite3 support"
        }


def check_sqlite_integrity(db_path: str = "stlms.db") -> dict:
    """Check SQLite database integrity."""
    if not os.path.isfile(db_path):
        _warn(f"Database not found: {db_path}")
        return {
            "name": "Database Integrity",
            "status": "WARN",
            "detail": "No database file found — will be created on first run",
            "recommendation": "Run 'python3 stlms.py setup' or 'python3 stlms.py run'"
        }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()

        if result == "ok":
            _ok(f"Database integrity: {result}")
            return {
                "name": "Database Integrity",
                "status": "PASS",
                "detail": result,
                "recommendation": None
            }
        else:
            _fail(f"Database integrity: {result}")
            return {
                "name": "Database Integrity",
                "status": "FAIL",
                "detail": result,
                "recommendation": "Run 'python3 stlms.py reset' to rebuild the database"
            }
    except Exception as e:
        _fail(f"Database check failed: {e}")
        return {
            "name": "Database Integrity",
            "status": "FAIL",
            "detail": str(e),
            "recommendation": "Run 'python3 stlms.py reset' to rebuild the database"
        }


def check_disk_space() -> dict:
    """Check available disk space."""
    try:
        stat = shutil.disk_usage(REPO_ROOT)
        free_gb = stat.free / (1024 ** 3)
        total_gb = stat.total / (1024 ** 3)

        if free_gb > 1.0:
            _ok(f"Disk space: {free_gb:.1f} GB free of {total_gb:.1f} GB")
            status = "PASS"
            rec = None
        elif free_gb > 0.1:
            _warn(f"Disk space: {free_gb:.1f} GB free of {total_gb:.1f} GB (low)")
            status = "WARN"
            rec = "Consider freeing disk space"
        else:
            _fail(f"Disk space: {free_gb:.1f} GB free of {total_gb:.1f} GB (critical)")
            status = "FAIL"
            rec = "Free disk space immediately"

        return {
            "name": "Disk Space",
            "status": status,
            "detail": f"{free_gb:.1f} GB free of {total_gb:.1f} GB",
            "recommendation": rec
        }
    except Exception as e:
        _warn(f"Could not check disk space: {e}")
        return {
            "name": "Disk Space",
            "status": "WARN",
            "detail": str(e),
            "recommendation": None
        }


def check_memory() -> dict:
    """Check available memory."""
    try:
        import resource
        # Check if we can get memory info
        usage = resource.getrusage(resource.RUSAGE_SELF)
        max_mb = usage.ru_maxrss / 1024  # KB to MB on Linux
        _info(f"Process max memory: {max_mb:.1f} MB")
        return {
            "name": "Memory",
            "status": "PASS",
            "detail": f"{max_mb:.1f} MB max RSS",
            "recommendation": None
        }
    except Exception:
        _info("Memory check not available on this system")
        return {
            "name": "Memory",
            "status": "INFO",
            "detail": "Not available",
            "recommendation": None
        }


def check_config() -> dict:
    """Check if configuration exists."""
    config_dir = os.path.join(str(Path.home()), ".stlms")
    config_file = os.path.join(config_dir, "config.json")
    local_config = os.path.join(REPO_ROOT, "stlms_config.json")

    found = False
    path = ""

    if os.path.isfile(config_file):
        found = True
        path = config_file
    elif os.path.isfile(local_config):
        found = True
        path = local_config

    if found:
        try:
            with open(path) as f:
                cfg = json.load(f)
            symbol = cfg.get("symbol", "?")
            tf = cfg.get("timeframe", "?")
            _ok(f"Config: {path} ({symbol} {tf})")
            return {
                "name": "Configuration",
                "status": "PASS",
                "detail": f"Found at {path} — {symbol} {tf}",
                "recommendation": None
            }
        except Exception as e:
            _warn(f"Config exists but could not be read: {e}")
            return {
                "name": "Configuration",
                "status": "WARN",
                "detail": str(e),
                "recommendation": "Delete config file and run setup again"
            }
    else:
        _warn("No configuration found — defaults will be used")
        return {
            "name": "Configuration",
            "status": "WARN",
            "detail": "Not found — using defaults",
            "recommendation": "Run 'python3 stlms.py setup' to create config"
        }


def check_imports() -> dict:
    """Check all core modules can import."""
    _info("Checking module imports...")

    modules_to_check = [
        "stlms",
        "stlms.core.shell",
        "stlms.core.constants",
        "stlms.core.types",
        "stlms.core.utils",
        "stlms.core.validators",
        "stlms.core.exceptions",
        "stlms.core.memory",
        "stlms.foundation.config_manager",
        "stlms.sqlite.connection",
        "stlms.sqlite.manager",
        "stlms.snapshot.manager",
        "stlms.snapshot.registry",
        "stlms.market.fixture",
        "stlms.market.artifact",
        "stlms.market.package",
        "stlms.market.validator",
        "stlms.market.consumer",
        "stlms.market.collection",
        "stlms.truth.point",
        "stlms.truth.package",
        "stlms.truth.validator",
        "stlms.truth.consumer",
        "stlms.structure.line",
        "stlms.structure.wave",
        "stlms.structure.cage",
        "stlms.evidence.bus",
        "stlms.clone.engine",
        "stlms.statistics.engine",
        "stlms.bag.engine",
        "stlms.knowledge.engine",
        "stlms.prediction.engine",
        "stlms.schema.engine",
        "stlms.recommendation.engine",
        "stlms.simulation.engine",
        "stlms.consumer.engine",
        "stlms.bench.engine",
        "stlms.governance.engine",
        "stlms.integration.engine",
        "stlms.distance.engine",
        "stlms.trade.engine",
        "stlms.position.engine",
    ]

    passed = 0
    failed = []
    for mod_name in modules_to_check:
        try:
            __import__(mod_name)
            passed += 1
        except Exception as e:
            failed.append((mod_name, str(e)))

    if failed:
        for name, err in failed:
            _fail(f"Import failed: {name} — {err}")
    else:
        _ok(f"All {passed} core modules import successfully")

    status = "PASS" if not failed else "WARN"
    return {
        "name": "Module Imports",
        "status": status,
        "detail": f"{passed}/{len(modules_to_check)} modules imported",
        "recommendation": None if not failed else "Check that all module files exist and have no syntax errors",
        "failed_modules": [f[0] for f in failed] if failed else []
    }


def check_pipeline() -> dict:
    """Check pipeline can run end-to-end."""
    _info("Checking pipeline execution...")
    try:
        from stlms.core.shell import STLMSShell
        shell = STLMSShell()
        result = shell.generate(candle_count=50)
        status = result.get("status", "UNKNOWN")
        stages = result.get("stages_executed", 0)
        total = result.get("stages_total", "?")

        if status == "COMPLETE":
            _ok(f"Pipeline: {stages}/{total} stages — {status}")
            return {
                "name": "Pipeline",
                "status": "PASS",
                "detail": f"{stages}/{total} stages completed",
                "recommendation": None
            }
        else:
            _warn(f"Pipeline: {stages}/{total} stages — {status}")
            return {
                "name": "Pipeline",
                "status": "WARN",
                "detail": f"Status: {status}, {stages}/{total} stages",
                "recommendation": "Check logs for pipeline issues"
            }
    except Exception as e:
        _fail(f"Pipeline failed: {e}")
        return {
            "name": "Pipeline",
            "status": "FAIL",
            "detail": str(e),
            "recommendation": "Run 'python3 stlms.py run' manually and check for issues"
        }


def check_network() -> dict:
    """Check network connectivity (optional)."""
    _info("Checking network connectivity...")
    try:
        import socket
        socket.setdefaulttimeout(5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        _ok("Network: connected")
        return {
            "name": "Network",
            "status": "PASS",
            "detail": "Internet accessible",
            "recommendation": None
        }
    except Exception:
        _warn("Network: not available")
        return {
            "name": "Network",
            "status": "WARN",
            "detail": "No internet — offline mode only",
            "recommendation": "Network is optional for ST-LMS (uses fixture data)"
        }


def check_directories() -> dict:
    """Check project directory structure."""
    required_dirs = [
        "stlms/core",
        "stlms/foundation",
        "stlms/sqlite",
        "stlms/market",
        "stlms/truth",
        "stlms/structure",
        "stlms/evidence",
        "stlms/clone",
        "stlms/statistics",
        "stlms/bag",
        "stlms/knowledge",
        "stlms/prediction",
        "stlms/schema",
        "stlms/recommendation",
        "stlms/simulation",
        "stlms/consumer",
        "stlms/bench",
        "stlms/governance",
        "stlms/integration",
        "stlms/snapshot",
        "stlms/cli",
        "stlms/distance",
        "stlms/trade",
        "stlms/position",
    ]

    missing = []
    for d in required_dirs:
        full_path = os.path.join(REPO_ROOT, d)
        if not os.path.isdir(full_path):
            missing.append(d)

    if missing:
        for d in missing:
            _fail(f"Missing directory: {d}")
        return {
            "name": "Directory Structure",
            "status": "FAIL",
            "detail": f"Missing {len(missing)} directories",
            "recommendation": "Project may be incomplete — check installation",
            "missing": missing
        }
    else:
        _ok(f"All {len(required_dirs)} core directories present")
        return {
            "name": "Directory Structure",
            "status": "PASS",
            "detail": f"{len(required_dirs)} directories present",
            "recommendation": None
        }


def run_doctor() -> None:
    """Run full doctor diagnostic."""
    _banner()

    results = []

    _section("System Checks")
    results.append(check_python())
    results.append(check_disk_space())
    results.append(check_memory())
    results.append(check_network())

    _section("Project Checks")
    results.append(check_directories())
    results.append(check_config())

    _section("Database Checks")
    results.append(check_sqlite_available())

    try:
        from stlms.cli.zeroconfig import load_config
        cfg = load_config()
        db_path = cfg.get("db_path", "stlms.db")
    except Exception:
        db_path = "stlms.db"

    results.append(check_sqlite_integrity(db_path))

    _section("Module Checks")
    results.append(check_imports())

    _section("Runtime Checks")
    results.append(check_pipeline())

    # ── Score ──────────────────────────────────────────────────
    _section("Diagnostic Summary")

    score = 0
    max_score = 0
    for r in results:
        max_score += 2
        if r["status"] == "PASS":
            score += 2
        elif r["status"] == "WARN":
            score += 1
        # FAIL = 0

    pct = (score / max_score * 100) if max_score > 0 else 0

    print()
    if pct >= 90:
        print(f"  HEALTH SCORE: {pct:.0f}%  [EXCELLENT]")
    elif pct >= 70:
        print(f"  HEALTH SCORE: {pct:.0f}%  [GOOD]")
    elif pct >= 50:
        print(f"  HEALTH SCORE: {pct:.0f}%  [FAIR]")
    else:
        print(f"  HEALTH SCORE: {pct:.0f}%  [NEEDS ATTENTION]")

    print()

    # ── Summary table ──────────────────────────────────────────
    print(f"  {'Check':30s} {'Status':>8s}")
    print(f"  {'-'*30} {'-'*8}")
    for r in results:
        status = r["status"]
        print(f"  {r['name']:30s} {status:>8s}")
    print()

    # ── Recommendations ────────────────────────────────────────
    recommendations = [r for r in results if r.get("recommendation")]
    if recommendations:
        print("  Recommendations:")
        for r in recommendations:
            print(f"    - [{r['status']}] {r['name']}: {r['recommendation']}")
        print()

    # ── Critical failures ──────────────────────────────────────
    critical = [r for r in results if r["status"] == "FAIL"]
    if critical:
        print(f"  Critical issues: {len(critical)}")
        for r in critical:
            print(f"    - {r['name']}: {r['detail']}")
        print()

    print("=" * 55)
    print("  Doctor complete.")
    if pct >= 90:
        print("  System is healthy. Ready for operation.")
    elif pct >= 70:
        print("  System is mostly healthy. Minor issues noted.")
    else:
        print("  System needs attention. See recommendations above.")
    print("=" * 55)
    print()


if __name__ == "__main__":
    run_doctor()
