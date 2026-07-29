"""
ST-LMS MCP TUI - Interactive Terminal UI
Interactive terminal UI for managing MCP servers.
"""

import sys
import os
import termios
import tty
import json
from pathlib import Path

def load_opencode_config():
    config_path = Path.home() / ".config" / "opencode" / "opencode.json"
    if not config_path.exists():
        return None, None
    with open(config_path) as f:
        return json.load(f), config_path

def save_opencode_config(config, config_path):
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

def render_menu(config):
    mcp = config.get("mcp", {})
    if not mcp:
        return ["No MCP servers configured"]
    lines = []
    lines.append("┌─────────────────────────────────────────────┐")
    lines.append("│  ST-LMS MCP Manager                          │")
    lines.append("├─────────────────────────────────────────────┤")
    for i, (name, info) in enumerate(mcp.items()):
        enabled = info.get("enabled", True)
        status = "[ON] " if enabled else "[OFF]"
        atype = info.get("type", "?")
        lines.append(f"│  {i}: {status} {name:20s} ({atype})")
    lines.append("├─────────────────────────────────────────────┤")
    lines.append("│  Commands:                                  │")
    lines.append("│    ↑/↓  Navigate     Space/Enter  Toggle    │")
    lines.append("│    q     Quit         0-9         Menu      │")
    lines.append("└─────────────────────────────────────────────┘")
    return lines

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch = sys.stdin.read(2)
            if ch == "[A":
                return "up"
            if ch == "[B":
                return "down"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def main():
    config, config_path = load_opencode_config()
    if not config:
        print("Config not found")
        sys.exit(1)

    mcp = config.get("mcp", {})
    names = list(mcp.keys())
    if not names:
        print("No MCP servers")
        sys.exit(0)

    selected = 0

    while True:
        os.system("clear")
        for line in render_menu(config):
            print(line)
        print(f"\n  Selected: {names[selected]}")

        key = get_key()

        if key == "q":
            break
        elif key == "up":
            selected = max(0, selected - 1)
        elif key == "down":
            selected = min(len(names) - 1, selected + 1)
        elif key in (" ", "\r", "\n"):
            name = names[selected]
            current = mcp[name].get("enabled", True)
            mcp[name]["enabled"] = not current
            save_opencode_config(config, config_path)
            new_state = "ON" if not current else "OFF"
            print(f"\n  {name} -> {new_state}")
            import time
            time.sleep(0.5)
        elif key.isdigit():
            idx = int(key)
            if idx < len(names):
                selected = idx

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled")
