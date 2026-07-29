"""
ST-LMS MCP CLI Manager
Add command-line commands to toggle MCP servers on/off.
"""

import sys
import json
import subprocess
from pathlib import Path

def load_opencode_config():
    config_path = Path.home() / ".config" / "opencode" / "opencode.json"
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f), config_path

def save_opencode_config(config, config_path):
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

def list_servers(config):
    mcp = config.get("mcp", {})
    if not mcp:
        print("No MCP servers configured")
        return
    print("MCP Servers:")
    for name, info in mcp.items():
        enabled = info.get("enabled", True)
        status = "ON" if enabled else "OFF"
        atype = info.get("type", "unknown")
        print(f"  [{status}] {name} ({atype})")

def status_server(config):
    mcp = config.get("mcp", {})
    if not mcp:
        print("No MCP servers configured")
        return
    for name, info in mcp.items():
        enabled = info.get("enabled", True)
        status = "ON" if enabled else "OFF"
        print(f"  {name}: {status}")

def on_server(config, name):
    mcp = config.get("mcp", {})
    if name not in mcp:
        print(f"Server not found: {name}")
        return
    mcp[name]["enabled"] = True
    print(f"[OK] {name} enabled")

def off_server(config, name):
    mcp = config.get("mcp", {})
    if name not in mcp:
        print(f"Server not found: {name}")
        return
    mcp[name]["enabled"] = False
    print(f"[OK] {name} disabled")

def toggle_server(config, name):
    mcp = config.get("mcp", {})
    if name not in mcp:
        print(f"Server not found: {name}")
        return
    current = mcp[name].get("enabled", True)
    mcp[name]["enabled"] = not current
    new_state = "ON" if not current else "OFF"
    print(f"[OK] {name} toggled to {new_state}")

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: mcp.py [list|on|off|toggle|status] [name]")
        sys.exit(1)

    config, config_path = load_opencode_config()
    cmd = args[0].lower()

    if cmd == "list":
        list_servers(config)
    elif cmd == "status":
        if len(args) > 1:
            status_server(config)
        else:
            for name in config.get("mcp", {}).keys():
                status_server(config)
    elif cmd == "on":
        if len(args) < 2:
            print("Usage: mcp.py on <name>")
            sys.exit(1)
        on_server(config, args[1])
        save_opencode_config(config, config_path)
        print("Restart opencode to apply changes")
    elif cmd == "off":
        if len(args) < 2:
            print("Usage: mcp.py off <name>")
            sys.exit(1)
        off_server(config, args[1])
        save_opencode_config(config, config_path)
        print("Restart opencode to apply changes")
    elif cmd == "toggle":
        if len(args) < 2:
            print("Usage: mcp.py toggle <name>")
            sys.exit(1)
        toggle_server(config, args[1])
        save_opencode_config(config, config_path)
        print("Restart opencode to apply changes")
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: mcp.py [list|on|off|toggle|status] [name]")
        sys.exit(1)

def run_cmd(args):
    """Entry point for Foundation CLI integration."""
    sys.argv = [sys.argv[0]] + args
    main()

if __name__ == "__main__":
    main()
