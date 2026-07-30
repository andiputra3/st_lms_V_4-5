"""
ST-LMS v4 — Zero-Config System
Auto-generates default config. No environment variables required.
Read config from ~/.stlms/config.json or ./stlms_config.json.
"""

import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "symbol": "BTCUSDT",
    "timeframe": "1m",
    "candle_count": 48000,
    "db_path": "stlms.db",
    "version": "4.0.0",
}


def _find_config() -> dict | None:
    """Search for config in standard locations. Returns dict or None."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    search_paths = [
        os.path.join(str(Path.home()), ".stlms", "config.json"),
        os.path.join(repo_root, "stlms_config.json"),
    ]

    for path in search_paths:
        if os.path.isfile(path):
            try:
                with open(path) as f:
                    cfg = json.load(f)
                if isinstance(cfg, dict) and cfg:
                    return cfg
            except (json.JSONDecodeError, IOError):
                continue

    return None


def _save_config(cfg: dict) -> None:
    """Save config to ~/.stlms/config.json."""
    config_dir = os.path.join(str(Path.home()), ".stlms")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=2)


def load_config() -> dict:
    """
    Load configuration. Returns a dict with all config keys guaranteed.
    Merges found config with defaults — found values override defaults.
    Auto-generates default config file if none exists.
    """
    found = _find_config()

    if found is None:
        _save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    merged.update({k: v for k, v in found.items() if k in DEFAULT_CONFIG})
    return merged


def get_config_path() -> str | None:
    """Return the path to the active config file, or None if not found."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    search_paths = [
        os.path.join(str(Path.home()), ".stlms", "config.json"),
        os.path.join(repo_root, "stlms_config.json"),
    ]
    for path in search_paths:
        if os.path.isfile(path):
            return path
    return None


def reset_config() -> None:
    """Reset config to defaults."""
    _save_config(DEFAULT_CONFIG)


if __name__ == "__main__":
    cfg = load_config()
    print("Configuration loaded:")
    for k, v in cfg.items():
        print(f"  {k}: {v}")
    print(f"  Source: {get_config_path() or 'defaults'}")
