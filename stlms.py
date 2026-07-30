#!/usr/bin/env python3
"""
ST-LMS v4 — Market Evolution Operating System
Single entry point. Just run: python3 stlms.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERSION = "4.0.0"


def _banner():
    print()
    print("=" * 45)
    print("   ST-LMS v4 — Market Evolution OS")
    print("=" * 45)
    print()


def _print_header(title: str):
    print()
    print("-" * 45)
    print(f"  {title}")
    print("-" * 45)
    print()


def _print_ok(msg: str):
    print(f"  [OK] {msg}")


def _print_info(msg: str):
    print(f"  [i]  {msg}")


def _print_warn(msg: str):
    print(f"  [!]  {msg}")


def _progress(msg: str):
    print(f"  ... {msg}")


def cmd_help():
    """Show help."""
    print("""
ST-LMS v4 — Market Evolution Operating System
=============================================

USAGE:
    python3 stlms.py                 Interactive menu
    python3 stlms.py <command>       Run a specific command

COMMANDS:
    setup         Auto-create venv, install deps, init SQLite, health check
    run           Run full pipeline with defaults
    live          Run pipeline + live market observation
    replay        Replay historical data
    statistics    Show all statistics
    dashboard     Start web dashboard
    knowledge     Show knowledge layer
    prediction    Show market prediction
    simulation    Run simulation
    recommendation Show market intelligence report
    sqlite        SQLite table viewer
    snapshot      Show snapshots
    timeline      Show truth timeline
    health        Quick health check
    doctor        Comprehensive system diagnostic
    update        Update dependencies
    test          Run tests
    clean         Clean temporary files
    reset         Reset database
    stop          Stop web server
    version       Show version
    help          Show this help

EXAMPLES:
    python3 stlms.py                 Open interactive menu
    python3 stlms.py setup           First-time setup
    python3 stlms.py run             Run pipeline
    python3 stlms.py live            Live observation
""")


def cmd_version():
    """Show version."""
    print(f"ST-LMS v{VERSION}")
    print("Market Evolution Operating System")
    print("License: Proprietary")


def cmd_setup():
    """Auto-create venv, install deps, init SQLite, health check."""
    from stlms.cli.setup import run_setup
    run_setup()


def cmd_run():
    """Run full pipeline with defaults."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Pipeline Run")
    cfg = load_config()
    _progress(f"Symbol: {cfg['symbol']} | Timeframe: {cfg['timeframe']} | Candles: {cfg['candle_count']}")

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    _progress("Generating market data...")
    result = shell.generate(candle_count=cfg["candle_count"])
    status = result.get("status", "UNKNOWN")
    _print_ok(f"Pipeline complete — status: {status}")

    if result.get("stages_executed"):
        _print_info(f"Stages: {result['stages_executed']}/{result.get('stages_total', '?')}")

    pred = shell.prediction_current()
    if pred.get("available"):
        _print_info(f"Prediction: {pred.get('dominant_bias', 'N/A')}")

    rec = shell.recommendation_report()
    if rec.get("available"):
        _print_info(f"Confidence: {rec.get('confidence', 'N/A')}/100")

    shell.persist()
    _print_ok("Data persisted to SQLite")

    print()


def cmd_live():
    """Run pipeline + live market observation."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Live Market Observation")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    _progress("Generating initial data...")
    shell.generate(candle_count=cfg["candle_count"])

    _print_info("Live observation mode active")
    _print_info("Press Ctrl+C to stop")

    try:
        while True:
            obs = shell.get_observation(-1)
            if obs.get("available"):
                print(f"  ts={obs.get('ts')} close={obs.get('close')} st={obs.get('st_dir')} "
                      f"cage={obs.get('cage_status')} wave={obs.get('wave_structure')}")
            else:
                _print_warn("No observation available")
            import time
            time.sleep(5)
    except KeyboardInterrupt:
        print()
        _print_ok("Live observation stopped")
        shell.persist()


def cmd_replay():
    """Replay historical data."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Historical Replay")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    _progress(f"Generating {cfg['candle_count']} candles...")
    shell.generate(candle_count=cfg["candle_count"])

    timeline = shell.get_timeline()
    if not timeline:
        _print_warn("No timeline data available")
        return

    _print_info(f"Replaying {len(timeline)} points")
    for i, point in enumerate(timeline):
        if i % 10 == 0:
            print(f"  [{i:4d}] ts={point.get('ts')} close={point.get('close', 0):.2f} "
                  f"st={point.get('st_dir', '?')} cage={point.get('cage_status', '?')}")

    print()
    _print_ok("Replay complete")


def cmd_statistics():
    """Show all statistics."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Market Statistics")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    shell.generate(candle_count=cfg["candle_count"])

    stats = shell.statistics_market()
    if not stats.get("available"):
        _print_warn("No statistics available — run 'python3 stlms.py run' first")
        return

    print(f"  Symbol: {cfg['symbol']} | Timeframe: {cfg['timeframe']}")
    print()

    by_clone = stats.get("by_clone", {})
    if by_clone:
        for clone_id, clone_stats in by_clone.items():
            print(f"  ── {clone_id} ──")
            for k, v in clone_stats.items():
                if isinstance(v, float):
                    print(f"    {k:20s}: {v:.4f}")
                else:
                    print(f"    {k:20s}: {v}")
            print()

    if not by_clone:
        for k, v in stats.items():
            if k in ("available", "by_clone"):
                continue
            if isinstance(v, float):
                print(f"  {k:20s}: {v:.4f}")
            else:
                print(f"  {k:20s}: {v}")

    print()


def cmd_dashboard():
    """Start web dashboard."""
    _banner()
    _print_header("Web Dashboard")

    try:
        from stlms.web.app import start_server
        _print_info("Starting web dashboard at http://localhost:8050")
        _print_info("Press Ctrl+C to stop")
        start_server(port=8050)
    except ImportError:
        _print_warn("Web dashboard module not available")
        _print_info("Ensure stlms.web is installed")
    except Exception as e:
        _print_warn(f"Could not start dashboard: {e}")


def cmd_knowledge():
    """Show knowledge layer."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Knowledge Layer")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    shell.generate(candle_count=cfg["candle_count"])

    academy = shell.knowledge_academy()
    if academy:
        print(f"  Academy buckets: {len(academy)}")
        for bucket in academy[:5]:
            print(f"    - {bucket}")
    else:
        _print_info("No academy data — run 'python3 stlms.py run' first")

    oracle = shell.knowledge_oracle()
    if oracle:
        print(f"  Oracle match: {oracle.get('match', 'N/A')} (score: {oracle.get('score', 0)})")

    hivemind = shell.knowledge_hivemind()
    if hivemind:
        print(f"  HiveMind: {hivemind.get('dominant_bias', 'N/A')} "
              f"(intelligence: {hivemind.get('intelligence_score', 0)})")

    print()


def cmd_prediction():
    """Show prediction."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Market Prediction")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    shell.generate(candle_count=cfg["candle_count"])

    pred = shell.prediction_current()
    if not pred.get("available"):
        _print_warn("No prediction available — run 'python3 stlms.py run' first")
        return

    print(f"  Symbol:     {cfg['symbol']}")
    print(f"  Timeframe:  {cfg['timeframe']}")
    print(f"  Bias:       {pred.get('dominant_bias', 'N/A')}")
    print()

    possibilities = pred.get("possibilities", [])
    if possibilities:
        print("  Possibilities:")
        print(f"  {'Type':15s} {'Probability':>12s}  {'Confidence':>12s}")
        print(f"  {'-'*15} {'-'*12}  {'-'*12}")
        for p in possibilities:
            prob = p.get("probability", 0)
            conf = p.get("confidence", "N/A")
            print(f"  {p.get('type', '?'):15s} {prob*100:>10.0f}%  {str(conf):>12s}")

    print()


def cmd_simulation():
    """Run simulation."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Simulation")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    shell.generate(candle_count=cfg["candle_count"])

    sim = shell.simulation_results()
    if not sim.get("available"):
        _print_warn("No simulation data — run 'python3 stlms.py run' first")
        return

    print(f"  Symbol:     {cfg['symbol']}")
    print(f"  Timeframe:  {cfg['timeframe']}")
    print()

    for k, v in sim.items():
        if k == "available":
            continue
        if isinstance(v, dict):
            print(f"  ── {k} ──")
            for sk, sv in v.items():
                if isinstance(sv, float):
                    print(f"    {sk:20s}: {sv:.4f}")
                else:
                    print(f"    {sk:20s}: {sv}")
        elif isinstance(v, float):
            print(f"  {k:20s}: {v:.4f}")
        else:
            print(f"  {k:20s}: {v}")

    print()


def cmd_recommendation():
    """Show market intelligence report."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Market Intelligence Report")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    shell.generate(candle_count=cfg["candle_count"])

    rec = shell.recommendation_report()
    if not rec.get("available"):
        _print_warn("No recommendation available — run 'python3 stlms.py run' first")
        return

    print(f"  Symbol:     {cfg['symbol']}")
    print(f"  Timeframe:  {cfg['timeframe']}")
    print(f"  Confidence: {rec.get('confidence', 'N/A')}/100")
    print()

    for k, v in rec.items():
        if k in ("available", "confidence"):
            continue
        if isinstance(v, dict):
            print(f"  ── {k} ──")
            for sk, sv in v.items():
                print(f"    {sk:20s}: {sv}")
        elif isinstance(v, list):
            print(f"  {k:20s}: [{len(v)} items]")
        else:
            print(f"  {k:20s}: {v}")

    print()
    print("  DISCLAIMER: Market Intelligence Report.")
    print("  NOT a trading signal. NOT financial advice.")
    print()


def cmd_sqlite():
    """SQLite table viewer."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("SQLite Explorer")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    tables = shell.sqlite_tables()
    if not tables:
        _print_warn("No tables found — run 'python3 stlms.py run' first")
        return

    print(f"  Database: {cfg.get('db_path', 'stlms.db')}")
    print(f"  {'Table':30s} {'Rows':>8s}")
    print(f"  {'-'*30} {'-'*8}")
    for t in tables:
        print(f"  {t['name']:30s} {t['rows']:>8d}")
    print()


def cmd_snapshot():
    """Show snapshots."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Snapshots")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    shell.generate(candle_count=cfg["candle_count"])

    snaps = shell.snapshots()
    if not snaps:
        _print_warn("No snapshots available — run 'python3 stlms.py run' first")
        return

    for snap_type, cards in snaps.items():
        print(f"  {snap_type}: {len(cards)} card(s)")
        for card in cards[:3]:
            print(f"    - {card}")

    print()


def cmd_timeline():
    """Show truth timeline."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Truth Timeline")
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    shell.generate(candle_count=cfg["candle_count"])

    points = shell.truth_points
    if not points:
        _print_warn("No truth points available — run 'python3 stlms.py run' first")
        return

    print(f"  Symbol: {cfg['symbol']} | Total points: {len(points)}")
    print()
    print(f"  {'Index':>6s} {'Timestamp':>12s} {'Close':>10s} {'ST':>6s} {'Color':>6s} {'Flip':>6s}")
    print(f"  {'-'*6} {'-'*12} {'-'*10} {'-'*6} {'-'*6} {'-'*6}")

    recent = points[-20:]
    for tp in recent:
        idx = getattr(tp, "index", "?")
        ts = getattr(tp, "ts", 0)
        close = getattr(tp, "close", 0)
        st = getattr(tp, "st", 0)
        color = getattr(tp, "st_color", "?")
        flip = "YES" if getattr(tp, "flip", False) else ""
        print(f"  {str(idx):>6s} {ts:>12d} {close:>10.2f} {st:>6.1f} {color:>6s} {flip:>6s}")

    print()


def cmd_health():
    """Quick health check."""
    from stlms.cli.zeroconfig import load_config
    _banner()
    _print_header("Health Check")
    cfg = load_config()

    checks = {}

    import sqlite3
    try:
        db_path = cfg.get("db_path", "stlms.db")
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
        checks["SQLite"] = True
    except Exception as e:
        checks["SQLite"] = False
        _print_warn(f"SQLite: {e}")

    import sys
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks["Python"] = sys.version_info >= (3, 10)
    _print_info(f"Python: {py_ver}")

    for name, ok in checks.items():
        if ok:
            _print_ok(f"{name}: OK")
        else:
            _print_warn(f"{name}: ISSUE")

    print()


def cmd_doctor():
    """Comprehensive system diagnostic."""
    from stlms.cli.doctor import run_doctor
    run_doctor()


def cmd_update():
    """Update dependencies."""
    _banner()
    _print_header("Update")

    import subprocess
    _progress("Updating dependencies...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            _print_ok("pip updated")
        else:
            _print_warn("pip update skipped")
    except Exception:
        _print_warn("Could not update pip")

    _print_info("ST-LMS uses stdlib only — no additional packages required")
    _print_ok("Update complete")


def cmd_test():
    """Run full test suite."""
    _banner()
    _print_header("ST-LMS Testing Ecosystem")

    import subprocess
    repo_root = os.path.dirname(os.path.abspath(__file__))

    _progress("Running all 276 tests...")
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "stlms/tests", "-v"],
        capture_output=True, text=True,
        cwd=repo_root
    )
    
    # Show summary
    lines = result.stdout.strip().split('\n')
    for line in lines[-10:]:
        print(f"  {line}")
    
    if result.returncode == 0:
        _print_ok("ST-LMS is healthy — all tests passed")
    else:
        _print_warn("Some tests failed — check output above")
        for line in lines:
            if 'FAIL' in line or 'ERROR' in line:
                print(f"  {line}")


def cmd_clean():
    """Clean temporary files."""
    _banner()
    _print_header("Clean")

    import shutil
    cleaned = 0

    pycache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__pycache__")
    if os.path.isdir(pycache):
        shutil.rmtree(pycache, ignore_errors=True)
        cleaned += 1
        _print_ok("Removed __pycache__")

    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__))):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                shutil.rmtree(path, ignore_errors=True)
                cleaned += 1
        for f in files:
            if f.endswith(".pyc") or f.endswith(".pyo"):
                os.remove(os.path.join(root, f))
                cleaned += 1

    _print_ok(f"Cleaned {cleaned} item(s)")


def cmd_reset():
    """Reset database."""
    _banner()
    _print_header("Reset Database")
    cfg = {}
    try:
        from stlms.cli.zeroconfig import load_config
        cfg = load_config()
    except Exception:
        pass

    db_path = cfg.get("db_path", "stlms.db")
    if os.path.exists(db_path):
        import time as _time
        backup = f"{db_path}.backup.{int(_time.time())}"
        os.rename(db_path, backup)
        _print_info(f"Database backed up to {backup}")

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(db_path=db_path)
    shell.generate(candle_count=cfg.get("candle_count", 48000))
    shell.persist()
    _print_ok("Database reset complete")


def cmd_stop():
    """Stop web server."""
    _banner()
    _print_header("Stop Server")

    import signal
    import subprocess

    try:
        result = subprocess.run(
            ["pgrep", "-f", "stlms.*dashboard"],
            capture_output=True, text=True
        )
        pids = result.stdout.strip().split()
        if pids:
            for pid in pids:
                os.kill(int(pid), signal.SIGTERM)
                _print_ok(f"Stopped process {pid}")
        else:
            _print_info("No running dashboard found")
    except Exception as e:
        _print_warn(f"Could not stop server: {e}")


COMMANDS = {
    "setup": cmd_setup,
    "run": cmd_run,
    "live": cmd_live,
    "replay": cmd_replay,
    "statistics": cmd_statistics,
    "dashboard": cmd_dashboard,
    "knowledge": cmd_knowledge,
    "prediction": cmd_prediction,
    "simulation": cmd_simulation,
    "recommendation": cmd_recommendation,
    "sqlite": cmd_sqlite,
    "snapshot": cmd_snapshot,
    "timeline": cmd_timeline,
    "health": cmd_health,
    "doctor": cmd_doctor,
    "update": cmd_update,
    "test": cmd_test,
    "clean": cmd_clean,
    "reset": cmd_reset,
    "stop": cmd_stop,
    "version": cmd_version,
    "help": cmd_help,
}


def main():
    if len(sys.argv) < 2:
        from stlms.cli.menu import run_menu
        run_menu()
        return

    cmd = sys.argv[1].lower()

    if cmd in COMMANDS:
        try:
            COMMANDS[cmd]()
        except KeyboardInterrupt:
            print()
            _print_info("Interrupted by user")
        except Exception as e:
            print()
            _print_warn(f"Something went wrong: {e}")
            _print_info("Try 'python3 stlms.py doctor' for diagnostics")
    else:
        print(f"Unknown command: '{cmd}'")
        print("Type 'python3 stlms.py help' for available commands.")
        sys.exit(1)


if __name__ == "__main__":
    main()
