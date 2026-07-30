"""
ST-LMS v4 — Setup System
Auto-detects environment, creates venv, initializes database, runs health check.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)


def _banner():
    print()
    print("=" * 50)
    print("   ST-LMS v4 — Setup")
    print("   Market Evolution Operating System")
    print("=" * 50)
    print()


def _print_ok(msg: str):
    print(f"  [OK] {msg}")


def _print_info(msg: str):
    print(f"  [i]  {msg}")


def _print_warn(msg: str):
    print(f"  [!]  {msg}")


def _progress(msg: str):
    print(f"  ... {msg}")


def _check_python() -> bool:
    """Verify Python 3.10+."""
    _progress("Checking Python version...")
    ver = sys.version_info
    version_str = f"{ver.major}.{ver.minor}.{ver.micro}"
    if ver >= (3, 10):
        _print_ok(f"Python {version_str}")
        return True
    else:
        _print_warn(f"Python {version_str} — need 3.10 or newer")
        return False


def _check_sqlite() -> bool:
    """Verify SQLite is available."""
    _progress("Checking SQLite...")
    try:
        import sqlite3
        ver = sqlite3.sqlite_version
        _print_ok(f"SQLite {ver}")
        return True
    except Exception as e:
        _print_warn(f"SQLite not available: {e}")
        return False


def _setup_venv() -> str:
    """Auto-detect or create virtual environment. Returns python executable path."""
    venv_dir = os.path.join(REPO_ROOT, "venv")

    # Already in a venv?
    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        _print_info("Already running inside a virtual environment")
        return sys.executable

    # Check if venv directory exists
    if os.path.isdir(venv_dir):
        venv_python = os.path.join(venv_dir, "bin", "python3")
        if os.path.isfile(venv_python):
            _print_ok("Virtual environment found")
            return venv_python
        venv_python = os.path.join(venv_dir, "bin", "python")
        if os.path.isfile(venv_python):
            _print_ok("Virtual environment found")
            return venv_python

    # Create venv
    _progress("Creating virtual environment...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", venv_dir],
            check=True, capture_output=True, text=True
        )
        _print_ok("Virtual environment created")

        venv_python = os.path.join(venv_dir, "bin", "python3")
        if not os.path.isfile(venv_python):
            venv_python = os.path.join(venv_dir, "bin", "python")

        # Upgrade pip
        subprocess.run(
            [venv_python, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True, text=True
        )
        _print_ok("pip upgraded")
        return venv_python
    except subprocess.CalledProcessError as e:
        _print_warn(f"Could not create virtual environment: {e}")
        _print_info("Falling back to system Python")
        return sys.executable


def _install_deps(python_exe: str) -> None:
    """ST-LMS uses stdlib only — verify, don't install."""
    _progress("Verifying dependencies...")
    _print_info("ST-LMS uses Python standard library only")
    _print_info("No external packages required")

    try:
        result = subprocess.run(
            [python_exe, "-c", "import sqlite3, json, csv, io, os, sys, pathlib, time, argparse, hashlib"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            _print_ok("All stdlib modules available")
        else:
            _print_warn("Some stdlib modules missing — check Python installation")
    except Exception as e:
        _print_warn(f"Dependency check failed: {e}")


def _init_database(db_path: str = "stlms.db") -> None:
    """Initialize SQLite database with required tables."""
    _progress("Initializing SQLite database...")
    try:
        from stlms.core.shell import STLMSShell
        shell = STLMSShell(db_path=db_path, enable_persistence=True)
        _print_ok(f"Database initialized: {db_path}")
    except Exception as e:
        _print_warn(f"Database initialization: {e}")


def _create_directories() -> None:
    """Create necessary directories."""
    _progress("Creating directories...")

    dirs = [
        os.path.join(REPO_ROOT, "data"),
        os.path.join(REPO_ROOT, "logs"),
        os.path.join(REPO_ROOT, "exports"),
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)

    _print_ok(f"Directories ready: data/, logs/, exports/")


def _generate_config() -> None:
    """Generate default config if none exists."""
    _progress("Checking configuration...")

    config_dir = os.path.join(str(Path.home()), ".stlms")
    config_file = os.path.join(config_dir, "config.json")

    if os.path.isfile(config_file):
        _print_ok("Configuration exists")
        return

    os.makedirs(config_dir, exist_ok=True)

    default_config = {
        "symbol": "BTCUSDT",
"timeframe": "1m",
"candle_count": 48000,
        "db_path": "stlms.db",
        "version": "4.0.0",
    }

    try:
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        _print_ok(f"Default config created: {config_file}")
    except Exception as e:
        _print_warn(f"Could not create config: {e}")

    # Also create a local config if none
    local_config = os.path.join(REPO_ROOT, "stlms_config.json")
    if not os.path.isfile(local_config):
        try:
            with open(local_config, "w") as f:
                json.dump(default_config, f, indent=2)
            _print_ok("Local config created: stlms_config.json")
        except Exception:
            pass


def _run_health_check() -> None:
    """Quick health check after setup."""
    _progress("Running health check...")
    try:
        from stlms.core.shell import STLMSShell
        shell = STLMSShell()
        health = shell.health()

        healthy = health.get("healthy", False)
        if healthy:
            _print_ok("Health check passed")
        else:
            _print_warn("Health check found issues")

        for name, ok in health.get("checks", {}).items():
            mark = "OK" if ok else "ISSUE"
            if ok:
                _print_ok(f"  {name}: {mark}")
            else:
                _print_warn(f"  {name}: {mark}")
    except Exception as e:
        _print_warn(f"Health check: {e}")


def run_setup() -> None:
    """Run full setup process."""
    _banner()

    _print_info("Auto-detecting environment...")
    print()

    python_ok = _check_python()
    if not python_ok:
        _print_warn("Python 3.10+ is required. Setup may not work correctly.")
        return

    sqlite_ok = _check_sqlite()
    if not sqlite_ok:
        _print_warn("SQLite is required. Setup may not work correctly.")
        return

    print()
    _print_info("Setting up virtual environment...")
    python_exe = _setup_venv()

    print()
    _print_info("Verifying dependencies...")
    _install_deps(python_exe)

    print()
    _print_info("Setting up directories and configuration...")
    _create_directories()
    _generate_config()

    print()
    _print_info("Initializing database...")
    _init_database()

    print()
    _print_info("Running health check...")
    _run_health_check()

    print()
    print("=" * 50)
    print("  SETUP COMPLETE")
    print("=" * 50)
    print()
    print("  Quick start:")
    print("    python3 stlms.py            Interactive menu")
    print("    python3 stlms.py run        Run pipeline")
    print("    python3 stlms.py dashboard  Web dashboard")
    print("    python3 stlms.py help       All commands")
    print()


if __name__ == "__main__":
    run_setup()
