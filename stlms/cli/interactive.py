"""
ST-LMS v4 — Interactive CLI
Lightweight interactive REPL using STLMSShell as shared core.

Designed for VPS 1.5GB — uses only print() and input().
No external TUI libraries. Supports 7 interaction modes.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

from stlms.core.shell import STLMSShell


class InteractiveCLI:
    """
    Interactive REPL loop with prompt 'stlms> '.

    Supports 7 interaction modes:
      1. NUMBER MODE    — type 1-9 to select from menu
      2. TEXT MODE      — type command name (status, truth, etc.)
      3. NATURAL CMD    — 'show btc statistics', 'replay point 42'
      4. WIZARD MODE    — 'help' or '?' shows guided menu
      5. QUICK CMD      — 'run', 'audit', 'export'
      6. ADVANCED MODE  — 'sqlite query SELECT...', 'pipeline stage 5'
      7. INTERACTIVE    — arrow keys to navigate menus (if supported)
    """

    def __init__(self, shell: STLMSShell):
        self._shell = shell
        self._running = False
        self._menu_index = 0

    def run(self) -> None:
        self._running = True
        self._print_banner()

        while self._running:
            try:
                raw = input("stlms> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not raw:
                continue

            self._dispatch(raw)

        print("Exiting ST-LMS Interactive CLI.")

    def _dispatch(self, raw: str) -> None:
        lower = raw.lower().strip()

        if lower in ("exit", "quit", "q"):
            self._running = False
            return

        # ── Mode 4: Wizard / Help ──────────────────────────────
        if lower in ("help", "h", "?"):
            self._cmd_help()
            return

        # ── Mode 1: Number menu ────────────────────────────────
        if lower.isdigit():
            idx = int(lower)
            self._dispatch_number(idx)
            return

        # ── Mode 6: Advanced — sqlite query / pipeline stage ───
        if lower.startswith("sqlite query"):
            sql = raw[len("sqlite query"):].strip()
            if sql:
                self._cmd_sqlite_query(sql)
            else:
                print("Usage: sqlite query <SELECT ...>")
            return

        if lower.startswith("pipeline stage"):
            stage = raw[len("pipeline stage"):].strip()
            self._cmd_pipeline_stage(stage)
            return

        # ── Mode 3: Natural language commands ──────────────────
        if any(kw in lower for kw in ("show", "display", "replay", "get", "fetch")):
            self._dispatch_natural(raw)
            return

        # ── Mode 5: Quick commands ─────────────────────────────
        if lower in ("run", "audit", "export"):
            self._dispatch_quick(lower, raw)
            return

        # ── Mode 2: Text command name ──────────────────────────
        self._dispatch_text(lower, raw)

    # ── Mode 1: Number dispatch ──────────────────────────────────

    def _dispatch_number(self, idx: int) -> None:
        menu = [
            ("status", self._cmd_status),
            ("truth", self._cmd_truth),
            ("timeline", self._cmd_timeline),
            ("events", self._cmd_events),
            ("structure", self._cmd_structure),
            ("wave", self._cmd_wave),
            ("cage", self._cmd_cage),
            ("distance", self._cmd_distance),
            ("statistics", self._cmd_statistics),
            ("prediction", self._cmd_prediction),
            ("recommendation", self._cmd_recommendation),
            ("simulation", self._cmd_simulation),
            ("sqlite", self._cmd_sqlite),
            ("pipeline", self._cmd_pipeline),
            ("export", self._cmd_export),
            ("help", self._cmd_help),
        ]

        if 1 <= idx <= len(menu):
            name, handler = menu[idx - 1]
            print(f"[{idx}] {name}")
            handler()
        else:
            print(f"Invalid menu index: {idx}. Type 'help' for menu.")

    # ── Mode 2: Text command name ────────────────────────────────

    def _dispatch_text(self, lower: str, raw: str) -> None:
        handlers = {
            "status": self._cmd_status,
            "truth": self._cmd_truth,
            "timeline": self._cmd_timeline,
            "events": self._cmd_events,
            "structure": self._cmd_structure,
            "wave": self._cmd_wave,
            "cage": self._cmd_cage,
            "distance": self._cmd_distance,
            "statistics": self._cmd_statistics,
            "prediction": self._cmd_prediction,
            "recommendation": self._cmd_recommendation,
            "simulation": self._cmd_simulation,
            "sqlite": self._cmd_sqlite,
            "pipeline": self._cmd_pipeline,
            "export": self._cmd_export,
        }

        if lower in handlers:
            handlers[lower]()
        else:
            print(f"Unknown command: '{raw}'. Type 'help' for available commands.")

    # ── Mode 3: Natural language dispatch ────────────────────────

    def _dispatch_natural(self, raw: str) -> None:
        lower = raw.lower()
        if "btc" in lower or "statistic" in lower:
            self._cmd_statistics()
        elif "point" in lower or "replay" in lower:
            self._cmd_timeline()
        elif "event" in lower or "market event" in lower:
            self._cmd_events()
        elif "cage" in lower:
            self._cmd_cage()
        elif "wave" in lower:
            self._cmd_wave()
        elif "prediction" in lower or "possibility" in lower:
            self._cmd_prediction()
        elif "report" in lower or "mir" in lower or "recommend" in lower:
            self._cmd_recommendation()
        elif "simulation" in lower or "simulate" in lower:
            self._cmd_simulation()
        elif "pipeline" in lower:
            self._cmd_pipeline()
        elif "sqlite" in lower or "table" in lower:
            self._cmd_sqlite()
        elif "export" in lower or "json" in lower:
            self._cmd_export()
        elif "status" in lower or "foundation" in lower:
            self._cmd_status()
        elif "truth" in lower or "sp" in lower:
            self._cmd_truth()
        elif "structure" in lower or "summary" in lower:
            self._cmd_structure()
        elif "distance" in lower:
            self._cmd_distance()
        else:
            print(f"Unrecognized natural command: '{raw}'")
            print("Try 'help' for available commands.")

    # ── Mode 5: Quick commands ───────────────────────────────────

    def _dispatch_quick(self, lower: str, raw: str) -> None:
        if lower == "run":
            print("Generating full pipeline...")
            result = self._shell.generate()
            print(json.dumps(result, default=str, indent=2))
        elif lower == "audit":
            self._cmd_health()
        elif lower == "export":
            self._cmd_export()

    # ── Command handlers ─────────────────────────────────────────

    def _cmd_status(self) -> None:
        print("=== Foundation Status ===")
        data = self._shell.status()
        for k, v in data.items():
            print(f"  {k}: {v}")

    def _cmd_health(self) -> None:
        print("=== Health Check ===")
        data = self._shell.health()
        print(f"  healthy: {data.get('healthy')}")
        for name, ok in data.get("checks", {}).items():
            mark = "OK" if ok else "FAIL"
            print(f"  [{mark}] {name}")
        for err in data.get("errors", []):
            print(f"  [ERR] {err}")

    def _cmd_truth(self) -> None:
        print("=== Current Truth (SP) ===")
        data = self._shell.truth_current()
        if not data.get("available", True):
            print("  No truth data available.")
            return
        for k, v in data.items():
            if k == "available":
                continue
            print(f"  {k}: {v}")

    def _cmd_timeline(self) -> None:
        print("=== Truth Timeline (last 20 points) ===")
        pts = self._shell.truth_points
        if not pts:
            print("  No truth points available.")
            return
        recent = pts[-20:]
        for tp in recent:
            st_color = getattr(tp, "st_color", "?")
            st = getattr(tp, "st", "?")
            close = getattr(tp, "close", 0)
            ts = getattr(tp, "ts", 0)
            flip = getattr(tp, "flip", "")
            flip_mark = f" FLIP:{flip}" if flip else ""
            print(f"  ts={ts} close={close:.2f} st={st} color={st_color}{flip_mark}")

    def _cmd_events(self) -> None:
        print("=== Recent Market Events ===")
        events = self._shell.truth_events()
        if not events:
            print("  No flip events found.")
            return
        for ev in events[-20:]:
            print(f"  ts={ev['ts']} flip={ev['flip']} st={ev['st']} close={ev['close']:.2f}")

    def _cmd_structure(self) -> None:
        print("=== Structure Summary ===")
        data = self._shell.structure_summary()
        if not data.get("available"):
            print("  No structure data available.")
            return
        print(f"  total_lines: {data.get('total_lines')}")
        print(f"  total_waves: {data.get('total_waves')}")
        cage = data.get("cage", {})
        if cage:
            print(f"  cage_status: {cage.get('status')}")
            print(f"  cage_upper: {cage.get('upper'):.2f}" if isinstance(cage.get('upper'), (int, float)) else f"  cage_upper: {cage.get('upper')}")
            print(f"  cage_lower: {cage.get('lower'):.2f}" if isinstance(cage.get('lower'), (int, float)) else f"  cage_lower: {cage.get('lower')}")
            print(f"  cage_pp: {cage.get('pp'):.2f}" if isinstance(cage.get('pp'), (int, float)) else f"  cage_pp: {cage.get('pp')}")
            print(f"  breakout: {cage.get('breakout')}")
            print(f"  pressure_up: {cage.get('pressure_up')}")
            print(f"  pressure_dn: {cage.get('pressure_dn')}")
        wave = data.get("current_wave", {})
        if wave:
            print(f"  wave_structure: {wave.get('structure')}")
            print(f"  wave_status: {wave.get('status')}")
            print(f"  wave_line_count: {wave.get('line_count')}")

    def _cmd_wave(self) -> None:
        print("=== Current Wave ===")
        data = self._shell.wave_current()
        if not data.get("available"):
            print("  No wave data available.")
            return
        for k, v in data.items():
            if k == "available":
                continue
            print(f"  {k}: {v}")

    def _cmd_cage(self) -> None:
        print("=== Current Cage ===")
        data = self._shell.cage_current()
        if not data.get("available"):
            print("  No cage data available.")
            return
        for k, v in data.items():
            if k == "available":
                continue
            if isinstance(v, float):
                print(f"  {k}: {v:.4f}")
            else:
                print(f"  {k}: {v}")

    def _cmd_distance(self) -> None:
        print("=== Distance Metrics ===")
        data = self._shell.distance_summary()
        if not data.get("available"):
            print("  No distance data available.")
            return
        for k, v in data.items():
            if k == "available":
                continue
            if isinstance(v, float):
                print(f"  {k}: {v:.4f}")
            else:
                print(f"  {k}: {v}")

    def _cmd_statistics(self) -> None:
        print("=== Statistics Summary ===")
        data = self._shell.statistics_market()
        if not data.get("available"):
            print("  No statistics available.")
            return
        by_clone = data.get("by_clone", {})
        for clone_id, stats in by_clone.items():
            print(f"  --- {clone_id} ---")
            for k, v in stats.items():
                if isinstance(v, float):
                    print(f"    {k}: {v:.4f}")
                else:
                    print(f"    {k}: {v}")

    def _cmd_prediction(self) -> None:
        print("=== Market Possibilities ===")
        data = self._shell.prediction_current()
        if not data.get("available"):
            print("  No prediction data available.")
            return
        for k, v in data.items():
            if k == "available":
                continue
            print(f"  {k}: {v}")

    def _cmd_recommendation(self) -> None:
        print("=== Full MIR Report ===")
        data = self._shell.recommendation_report()
        if not data.get("available"):
            print("  No recommendation available.")
            return
        for k, v in data.items():
            if k == "available":
                continue
            if isinstance(v, dict):
                print(f"  {k}:")
                for sk, sv in v.items():
                    print(f"    {sk}: {sv}")
            elif isinstance(v, list):
                print(f"  {k}: [{len(v)} items]")
            else:
                print(f"  {k}: {v}")

    def _cmd_simulation(self) -> None:
        print("=== Simulation Results ===")
        data = self._shell.simulation_results()
        if not data.get("available"):
            print("  No simulation data available.")
            return
        for k, v in data.items():
            if k == "available":
                continue
            if isinstance(v, dict):
                print(f"  --- {k} ---")
                for sk, sv in v.items():
                    if isinstance(sv, float):
                        print(f"    {sk}: {sv:.4f}")
                    else:
                        print(f"    {sk}: {sv}")
            else:
                print(f"  {k}: {v}")

    def _cmd_sqlite(self) -> None:
        print("=== SQLite Tables ===")
        tables = self._shell.sqlite_tables()
        if not tables:
            print("  No tables found.")
            return
        for t in tables:
            print(f"  {t['name']}: {t['rows']} rows")

    def _cmd_sqlite_query(self, sql: str) -> None:
        print(f"=== SQLite Query ===")
        print(f"  SQL: {sql}")
        result = self._shell.sqlite_query(sql)
        if "error" in result:
            print(f"  Error: {result['error']}")
            return
        rows = result.get("rows", [])
        total = result.get("total", len(rows))
        print(f"  Rows: {len(rows)} (total: {total})")
        for row in rows[:20]:
            print(f"  {row}")

    def _cmd_pipeline(self) -> None:
        print("=== Pipeline Status ===")
        data = self._shell.pipeline_status()
        for k, v in data.items():
            print(f"  {k}: {v}")

    def _cmd_pipeline_stage(self, stage: str) -> None:
        print(f"=== Pipeline Stage {stage} ===")
        report = self._shell.pipeline_status()
        stages = report.get("stages", [])
        if not stages:
            print("  No stage detail available.")
            return
        try:
            idx = int(stage) - 1
            if 0 <= idx < len(stages):
                s = stages[idx]
                for k, v in s.items():
                    print(f"  {k}: {v}")
            else:
                print(f"  Stage {stage} out of range (1-{len(stages)}).")
        except ValueError:
            print(f"  Invalid stage number: '{stage}'")

    def _cmd_export(self) -> None:
        print("=== Exporting to JSON ===")
        data = self._shell.export("json")
        print(data)

    def _cmd_help(self) -> None:
        print("ST-LMS Interactive CLI")
        print()
        print("┌─── Menu ───────────────────────────────────┐")
        print("│  1: status         Foundation status       │")
        print("│  2: truth          Current SP              │")
        print("│  3: timeline       Truth timeline (last 20)│")
        print("│  4: events         Recent market events    │")
        print("│  5: structure      Structure summary       │")
        print("│  6: wave           Current wave            │")
        print("│  7: cage           Current cage            │")
        print("│  8: distance       Distance metrics        │")
        print("│  9: statistics     Statistics summary      │")
        print("│ 10: prediction     Market possibilities    │")
        print("│ 11: recommendation Full MIR report         │")
        print("│ 12: simulation     Simulation results      │")
        print("│ 13: sqlite         SQLite tables           │")
        print("│ 14: pipeline       Pipeline status         │")
        print("│ 15: export         Export to JSON          │")
        print("│ 16: help           Show this help          │")
        print("└────────────────────────────────────────────┘")
        print()
        print("Quick commands: run, audit, export")
        print("Natural: 'show btc statistics', 'replay point 42'")
        print("Advanced: 'sqlite query SELECT ...'")
        print("Type 'exit' or 'quit' to leave.")
        print()

    # ── Banner ───────────────────────────────────────────────────

    def _print_banner(self) -> None:
        print("ST-LMS v4 — Interactive CLI")
        print(f"Symbol: {self._shell.symbol} | Timeframe: {self._shell.timeframe}")
        print("Type 'help' or '?' for menu, 'exit' to quit.")
        print()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="ST-LMS Interactive CLI")
    parser.add_argument("--db", default="stlms.db", help="SQLite database path")
    parser.add_argument("--symbol", default="BTCUSDT", help="Trading symbol")
    parser.add_argument("--timeframe", default="1m", help="Candle timeframe")
    parser.add_argument("--candles", type=int, default=500, help="Fixture candle count")
    args = parser.parse_args()

    shell = STLMSShell(
        db_path=args.db,
        symbol=args.symbol,
        timeframe=args.timeframe,
    )

    print("Generating fixture data...")
    gen_result = shell.generate(candle_count=args.candles)
    print(f"Generation status: {gen_result.get('status')}")
    print()

    cli = InteractiveCLI(shell)
    cli.run()


if __name__ == "__main__":
    main()
