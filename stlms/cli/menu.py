"""
ST-LMS v4 — Interactive Menu
Numbered menu system for the ST-LMS Market Evolution OS.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _clear_screen():
    """Clear terminal if supported."""
    if os.name == "posix":
        print("\033[2J\033[H", end="")


def _print_banner():
    print()
    print("=" * 45)
    print("   ST-LMS v4 — Market Evolution OS")
    print("=" * 45)
    print()


def _print_menu():
    print()
    print("  1. Live Market Observation")
    print("     Watch market data update in real time")
    print()
    print("  2. Replay Historical Data")
    print("     Step through historical candle data")
    print()
    print("  3. Market Statistics")
    print("     View clone performance and market statistics")
    print()
    print("  4. Knowledge Layer")
    print("     Academy, Oracle, and HiveMind intelligence")
    print()
    print("  5. Market Prediction")
    print("     See current market direction possibilities")
    print()
    print("  6. Simulation")
    print("     Run architecture and balance simulations")
    print()
    print("  7. Market Intelligence Report")
    print("     Full recommendation with confidence score")
    print()
    print("  8. Snapshot Viewer")
    print("     Browse saved market snapshots")
    print()
    print("  9. SQLite Explorer")
    print("     View database tables and row counts")
    print()
    print(" 10. Timeline Viewer")
    print("     Browse truth points and market structure")
    print()
    print(" 11. Web Dashboard")
    print("     Start interactive web dashboard")
    print()
    print(" 12. Health Check")
    print("     Quick system health verification")
    print()
    print(" 13. Doctor (Full Diagnostic)")
    print("     Comprehensive system diagnostic with score")
    print()
    print(" 14. Testing Center")
    print("     Run comprehensive market evolution tests")
    print()
    print(" 15. Settings")
    print("     View and edit configuration")
    print()
    print(" 16. Help")
    print("     Show command reference")
    print()
    print(" 17. Exit")
    print("     Exit ST-LMS")
    print()
    print("-" * 45)


def _run_command(cmd_name: str):
    """Dispatch to the main CLI command."""
    from stlms.cli.zeroconfig import load_config
    cfg = load_config()

    from stlms.core.shell import STLMSShell
    shell = STLMSShell(
        db_path=cfg.get("db_path", "stlms.db"),
        symbol=cfg["symbol"],
        timeframe=cfg["timeframe"],
    )

    if cmd_name == "live":
        print()
        print("-" * 45)
        print("  Live Market Observation")
        print("-" * 45)
        print()
        print(f"  Symbol: {cfg['symbol']} | Timeframe: {cfg['timeframe']}")
        print("  Generating data...")
        shell.generate(candle_count=cfg["candle_count"])
        print("  Observation active. Press Ctrl+C to stop.")
        print()
        try:
            import time
            while True:
                obs = shell.get_observation(-1)
                if obs.get("available"):
                    print(f"  ts={obs.get('ts')} close={obs.get('close')} st={obs.get('st_dir')} "
                          f"cage={obs.get('cage_status')} wave={obs.get('wave_structure')}")
                else:
                    print("  [i] Waiting for data...")
                time.sleep(5)
        except KeyboardInterrupt:
            print()
            print("  Observation stopped.")
            shell.persist()

    elif cmd_name == "replay":
        print()
        print("-" * 45)
        print("  Historical Replay")
        print("-" * 45)
        print()
        print(f"  Generating {cfg['candle_count']} candles...")
        shell.generate(candle_count=cfg["candle_count"])
        timeline = shell.get_timeline()
        if not timeline:
            print("  [i] No timeline data available")
            return
        print(f"  Replaying {len(timeline)} points")
        print()
        print(f"  {'Index':>6s} {'Timestamp':>12s} {'Close':>10s} {'Cage':>10s} {'Wave':>10s}")
        print(f"  {'-'*6} {'-'*12} {'-'*10} {'-'*10} {'-'*10}")
        for i, point in enumerate(timeline):
            if i % 10 == 0:
                print(f"  {i:>6d} {point.get('ts',0):>12d} {point.get('close',0):>10.2f} "
                      f"{str(point.get('cage_status','?')):>10s} {str(point.get('wave_structure','?')):>10s}")
        print()
        print("  Replay complete.")

    elif cmd_name == "statistics":
        print()
        print("-" * 45)
        print("  Market Statistics")
        print("-" * 45)
        print()
        shell.generate(candle_count=cfg["candle_count"])
        stats = shell.statistics_market()
        if not stats.get("available"):
            print("  [i] No statistics — run pipeline first")
            return
        by_clone = stats.get("by_clone", {})
        if by_clone:
            for clone_id, cs in by_clone.items():
                print(f"  ── {clone_id} ──")
                for k, v in cs.items():
                    if isinstance(v, float):
                        print(f"    {k:20s}: {v:.4f}")
                    else:
                        print(f"    {k:20s}: {v}")
                print()
        else:
            for k, v in stats.items():
                if k in ("available", "by_clone"):
                    continue
                print(f"  {k:20s}: {v}")

    elif cmd_name == "knowledge":
        print()
        print("-" * 45)
        print("  Knowledge Layer")
        print("-" * 45)
        print()
        shell.generate(candle_count=cfg["candle_count"])
        academy = shell.knowledge_academy()
        oracle = shell.knowledge_oracle()
        hivemind = shell.knowledge_hivemind()
        if academy:
            print(f"  Academy buckets: {len(academy)}")
            for b in academy[:5]:
                print(f"    - {b}")
        if oracle:
            print(f"  Oracle match: {oracle.get('match','?')} (score: {oracle.get('score',0)})")
        if hivemind:
            print(f"  HiveMind: {hivemind.get('dominant_bias','?')} (score: {hivemind.get('intelligence_score',0)})")
        if not academy and not oracle and not hivemind:
            print("  [i] No knowledge data — run pipeline first")

    elif cmd_name == "prediction":
        print()
        print("-" * 45)
        print("  Market Prediction")
        print("-" * 45)
        print()
        shell.generate(candle_count=cfg["candle_count"])
        pred = shell.prediction_current()
        if not pred.get("available"):
            print("  [i] No prediction — run pipeline first")
            return
        print(f"  Bias: {pred.get('dominant_bias','?')}")
        possibilities = pred.get("possibilities", [])
        if possibilities:
            print()
            print(f"  {'Type':15s} {'Probability':>12s}  {'Confidence':>12s}")
            print(f"  {'-'*15} {'-'*12}  {'-'*12}")
            for p in possibilities:
                prob = p.get("probability", 0)
                print(f"  {p.get('type','?'):15s} {prob*100:>10.0f}%  {str(p.get('confidence','?')):>12s}")

    elif cmd_name == "simulation":
        print()
        print("-" * 45)
        print("  Simulation")
        print("-" * 45)
        print()
        shell.generate(candle_count=cfg["candle_count"])
        sim = shell.simulation_results()
        if not sim.get("available"):
            print("  [i] No simulation — run pipeline first")
            return
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

    elif cmd_name == "recommendation":
        print()
        print("-" * 45)
        print("  Market Intelligence Report")
        print("-" * 45)
        print()
        shell.generate(candle_count=cfg["candle_count"])
        rec = shell.recommendation_report()
        if not rec.get("available"):
            print("  [i] No recommendation — run pipeline first")
            return
        print(f"  Confidence: {rec.get('confidence','?')}/100")
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

    elif cmd_name == "snapshot":
        print()
        print("-" * 45)
        print("  Snapshots")
        print("-" * 45)
        print()
        shell.generate(candle_count=cfg["candle_count"])
        snaps = shell.snapshots()
        if not snaps:
            print("  [i] No snapshots — run pipeline first")
            return
        for snap_type, cards in snaps.items():
            print(f"  {snap_type}: {len(cards)} card(s)")
            for card in cards[:3]:
                print(f"    - {card}")

    elif cmd_name == "sqlite":
        print()
        print("-" * 45)
        print("  SQLite Explorer")
        print("-" * 45)
        print()
        tables = shell.sqlite_tables()
        if not tables:
            print("  [i] No tables found — run pipeline first")
            return
        print(f"  Database: {cfg.get('db_path', 'stlms.db')}")
        print(f"  {'Table':30s} {'Rows':>8s}")
        print(f"  {'-'*30} {'-'*8}")
        for t in tables:
            print(f"  {t['name']:30s} {t['rows']:>8d}")

    elif cmd_name == "timeline":
        print()
        print("-" * 45)
        print("  Truth Timeline")
        print("-" * 45)
        print()
        shell.generate(candle_count=cfg["candle_count"])
        points = shell.truth_points
        if not points:
            print("  [i] No truth points — run pipeline first")
            return
        print(f"  Total points: {len(points)}")
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

    elif cmd_name == "dashboard":
        print()
        print("-" * 45)
        print("  Web Dashboard")
        print("-" * 45)
        print()
        try:
            from stlms.web.app import start_server
            print("  Starting at http://localhost:8050")
            print("  Press Ctrl+C to stop")
            start_server(port=8050)
        except ImportError:
            print("  [i] Web dashboard module not available")
        except Exception as e:
            print(f"  [!] Could not start: {e}")

    elif cmd_name == "health":
        print()
        print("-" * 45)
        print("  Health Check")
        print("-" * 45)
        print()
        try:
            import sqlite3 as _sq
            conn = _sq.connect(cfg.get("db_path", "stlms.db"))
            conn.execute("SELECT 1")
            conn.close()
            print("  [OK] SQLite: OK")
        except Exception as e:
            print(f"  [!] SQLite: {e}")
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"  [i]  Python: {py_ver}")
        print(f"  [i]  Symbol: {cfg['symbol']} | TF: {cfg['timeframe']}")
        print()

    elif cmd_name == "doctor":
        from stlms.cli.doctor import run_doctor
        run_doctor()

    elif cmd_name == "test":
        print()
        print("-" * 45)
        print("  ST-LMS Testing Center")
        print("-" * 45)
        print()
        print("  Test Categories:")
        print()
        print("    1.  Full Test Suite         — All 276 tests")
        print("    2.  Collection System       — Batch, continuity, provider")
        print("    3.  Observation Window      — Configurable sizes 100-5000")
        print("    4.  Living Objects          — All entities alive check")
        print("    5.  Market Evolution        — Line, Wave, DNA, Knowledge")
        print("    6.  Synchronization         — Observation, snapshot, memory sync")
        print("    7.  Replay                  — Historical + batch replay")
        print("    8.  SQLite                  — Persistence + queries")
        print("    9.  Performance             — 100-5000 observations")
        print("   10.  Stress                  — Continuous collection + batches")
        print("   11.  Health Check            — System diagnostic")
        print("   12.  Back to Main Menu")
        print()
        print("-" * 45)

        sub_choice = input("  Select [1-12]: ").strip()
        print()

        import subprocess
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        test_modules = []
        if sub_choice == "1":
            test_modules = ["discover", "-s", "stlms/tests"]
        elif sub_choice == "2":
            test_modules = ["stlms.tests.test_collection_system"]
        elif sub_choice == "3":
            test_modules = ["stlms.tests.test_observation_window"]
        elif sub_choice == "4":
            test_modules = ["stlms.tests.test_living_objects"]
        elif sub_choice == "5":
            test_modules = ["stlms.tests.test_market_evolution_comprehensive"]
        elif sub_choice == "6":
            test_modules = ["stlms.tests.test_market_evolution_comprehensive.TestMarketSynchronization"]
        elif sub_choice == "7":
            test_modules = ["stlms.tests.test_market_evolution_comprehensive.TestReplayEvolution"]
        elif sub_choice == "8":
            test_modules = ["stlms.tests.test_market_evolution_comprehensive.TestSQLiteEvolution"]
        elif sub_choice == "9":
            test_modules = ["stlms.tests.test_market_evolution_comprehensive.TestPerformanceAtScale"]
        elif sub_choice == "10":
            test_modules = ["stlms.tests.test_market_evolution_comprehensive.TestStress"]
        elif sub_choice == "11":
            from stlms.cli.doctor import run_doctor
            run_doctor()
            return
        elif sub_choice == "12":
            return
        else:
            print(f"  '{sub_choice}' is not valid.")
            return

        if sub_choice != "11":
            print("  Running tests...")
            print()
            cmd = [sys.executable, "-m", "unittest"] + test_modules + ["-v"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=repo_root
            )
            print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            if result.stderr and "Ran" not in result.stderr:
                print(result.stderr[-500:])

            if result.returncode == 0:
                print("  [OK] Tests passed — ST-LMS is healthy")
            else:
                print("  [!] Some tests did not pass")

    elif cmd_name == "settings":
        print()
        print("-" * 45)
        print("  Settings")
        print("-" * 45)
        print()
        print(f"  Symbol:       {cfg.get('symbol', 'BTCUSDT')}")
    print(f"  Timeframe:    {cfg.get('timeframe', '1m')}")
    print(f"  Candle Count: {cfg.get('candle_count', 48000)}")
        print(f"  Database:     {cfg.get('db_path', 'stlms.db')}")
        print(f"  Version:      {cfg.get('version', '4.0.0')}")
        print()
        print("  Config locations:")
        from pathlib import Path
        print(f"    ~/.stlms/config.json")
        print(f"    ./stlms_config.json")
        print()

    elif cmd_name == "help":
        print()
        print("  ST-LMS v4 Command Reference")
        print()
        print("  Interactive:   python3 stlms.py")
        print("  Run Pipeline:  python3 stlms.py run")
        print("  Live Watch:    python3 stlms.py live")
        print("  Statistics:    python3 stlms.py statistics")
        print("  Dashboard:     python3 stlms.py dashboard")
        print("  Doctor:        python3 stlms.py doctor")
        print("  All commands:  python3 stlms.py help")
        print()

    else:
        print(f"  Unknown option: {cmd_name}")


def run_menu():
    """Run the interactive numbered menu loop."""
    _print_banner()

    menu_map = {
        "1": "live",
        "2": "replay",
        "3": "statistics",
        "4": "knowledge",
        "5": "prediction",
        "6": "simulation",
        "7": "recommendation",
        "8": "snapshot",
        "9": "sqlite",
        "10": "timeline",
        "11": "dashboard",
        "12": "health",
        "13": "doctor",
        "14": "test",
        "15": "settings",
        "16": "help",
        "17": "exit",
    }

    text_map = {
        "live": "1", "observation": "1",
        "replay": "2", "history": "2",
        "statistics": "3", "stats": "3",
        "knowledge": "4",
        "prediction": "5", "predict": "5",
        "simulation": "6", "simulate": "6", "sim": "6",
        "recommendation": "7", "mir": "7", "report": "7", "recommend": "7",
        "snapshot": "8", "snapshots": "8", "snap": "8",
        "sqlite": "9", "sql": "9", "db": "9", "database": "9",
        "timeline": "10", "time": "10",
        "dashboard": "11", "dash": "11", "web": "11",
        "health": "12",
        "doctor": "13", "diagnostic": "13", "diagnose": "13",
        "test": "14", "testing": "14", "tests": "14",
        "settings": "15", "config": "15", "setting": "15",
        "help": "16", "?": "16", "h": "16",
        "exit": "17", "quit": "17", "q": "17", "e": "17",
    }

    while True:
        _print_menu()
        try:
            raw = input("  Select [1-17]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            print("  Exiting ST-LMS. Goodbye.")
            print()
            break

        if not raw:
            continue

        # Try direct number match
        if raw in menu_map:
            choice = raw
            cmd = menu_map[choice]
        # Try text match
        elif raw in text_map:
            choice = text_map[raw]
            cmd = menu_map[choice]
        else:
            print(f"  '{raw}' is not a valid selection. Try 1-16 or type a command name.")
            print()
            continue

        if cmd == "exit":
            print()
            print("  Exiting ST-LMS. Goodbye.")
            print()
            break

        try:
            _run_command(cmd)
        except KeyboardInterrupt:
            print()
            print("  Interrupted.")
        except Exception as e:
            print()
            print(f"  [!] Something went wrong: {e}")
            print("  [i]  Try 'python3 stlms.py doctor' for diagnostics")

        input("\n  Press Enter to continue...")
        _clear_screen()
        _print_banner()


if __name__ == "__main__":
    run_menu()
