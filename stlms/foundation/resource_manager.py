"""
ST-LMS v3 — Resource Manager
Foundation Core — Phase 1

VPS 1.5 GB RAM friendly resource monitoring.
"""

import os
import time
from typing import Optional

class ResourceManager:
    @staticmethod
    def memory_usage_mb() -> float:
        try:
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        except (ImportError, AttributeError):
            return 0.0

    @staticmethod
    def cpu_usage() -> float:
        try:
            return os.times()[0] / os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        except Exception:
            return 0.0

    @staticmethod
    def disk_usage(path: str = ".") -> dict:
        stat = os.statvfs(path)
        total = stat.f_frsize * stat.f_blocks
        free = stat.f_frsize * stat.f_bavail
        used = total - free
        return {
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
            "used_pct": round(used / total * 100, 1) if total > 0 else 0,
        }

    @staticmethod
    def is_vps_friendly(memory_limit_mb: float = 1536.0) -> tuple[bool, str]:
        mem = ResourceManager.memory_usage_mb()
        if mem > memory_limit_mb * 0.95:
            return False, f"CRITICAL: {mem:.1f}MB / {memory_limit_mb}MB (95%+)"
        if mem > memory_limit_mb * 0.85:
            return False, f"HIGH: {mem:.1f}MB / {memory_limit_mb}MB (85%+)"
        if mem > memory_limit_mb * 0.70:
            return True, f"WARN: {mem:.1f}MB / {memory_limit_mb}MB (70%+)"
        return True, f"OK: {mem:.1f}MB / {memory_limit_mb}MB"

    @staticmethod
    def status() -> dict:
        mem_ok, mem_msg = ResourceManager.is_vps_friendly()
        return {
            "memory_mb": round(ResourceManager.memory_usage_mb(), 1),
            "memory_status": mem_msg,
            "memory_ok": mem_ok,
            "cpu_seconds": round(ResourceManager.cpu_usage(), 2),
            "disk": ResourceManager.disk_usage(),
        }
