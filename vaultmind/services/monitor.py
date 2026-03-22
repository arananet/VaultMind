"""System monitor for VaultMind hardware health checks."""

from __future__ import annotations

import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SystemStatus:
    """Snapshot of system health metrics."""

    cpu_temp_c: float | None = None
    cpu_usage_percent: float | None = None
    memory_total_mb: int | None = None
    memory_used_mb: int | None = None
    disks: list[dict] = field(default_factory=list)
    raid_status: str | None = None
    battery_percent: float | None = None
    battery_charging: bool | None = None
    ollama_running: bool = False
    kiwix_running: bool = False
    uptime_seconds: float | None = None
    warnings: list[str] = field(default_factory=list)


def get_system_status() -> SystemStatus:
    """Collect system health metrics."""
    status = SystemStatus()

    # CPU temperature
    status.cpu_temp_c = _read_cpu_temp()
    if status.cpu_temp_c and status.cpu_temp_c > 80:
        status.warnings.append(f"CPU temperature critical: {status.cpu_temp_c}°C")

    # CPU usage
    status.cpu_usage_percent = _read_cpu_usage()

    # Memory
    mem = _read_memory()
    if mem:
        status.memory_total_mb = mem["total"]
        status.memory_used_mb = mem["used"]
        usage_pct = mem["used"] / mem["total"] * 100 if mem["total"] else 0
        if usage_pct > 90:
            status.warnings.append(f"Memory usage high: {usage_pct:.0f}%")

    # Disk space
    status.disks = _read_disk_space()
    for disk in status.disks:
        if disk.get("percent_used", 0) > 90:
            status.warnings.append(
                f"Disk {disk['mount']} nearly full: {disk['percent_used']}%"
            )

    # RAID / ZFS status
    status.raid_status = _read_raid_status()
    if status.raid_status and "DEGRADED" in status.raid_status.upper():
        status.warnings.append("RAID/ZFS array is DEGRADED — replace failed drive!")

    # Battery (if available)
    battery = _read_battery()
    if battery:
        status.battery_percent = battery["percent"]
        status.battery_charging = battery["charging"]
        if battery["percent"] < 20 and not battery["charging"]:
            status.warnings.append(
                f"Battery low: {battery['percent']}% — connect solar/charger"
            )

    # Service checks
    status.ollama_running = _check_service("ollama")
    status.kiwix_running = _check_service("kiwix")

    # Uptime
    status.uptime_seconds = _read_uptime()

    return status


def _read_cpu_temp() -> float | None:
    """Read CPU temperature from thermal zones."""
    thermal_path = Path("/sys/class/thermal/thermal_zone0/temp")
    if thermal_path.exists():
        try:
            raw = thermal_path.read_text().strip()
            return int(raw) / 1000.0
        except (ValueError, OSError):
            pass
    return None


def _read_cpu_usage() -> float | None:
    """Read CPU usage from /proc/stat (simplified)."""
    try:
        stat_path = Path("/proc/stat")
        if not stat_path.exists():
            return None
        line = stat_path.read_text().split("\n")[0]
        parts = line.split()
        if parts[0] != "cpu":
            return None
        values = [int(p) for p in parts[1:]]
        idle = values[3] if len(values) > 3 else 0
        total = sum(values)
        if total == 0:
            return None
        return round((1 - idle / total) * 100, 1)
    except Exception:
        return None


def _read_memory() -> dict | None:
    """Read memory info from /proc/meminfo."""
    meminfo_path = Path("/proc/meminfo")
    if not meminfo_path.exists():
        return None
    try:
        info = {}
        for line in meminfo_path.read_text().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                info[key.strip()] = int(val.strip().split()[0])  # kB
        total = info.get("MemTotal", 0) // 1024
        available = info.get("MemAvailable", 0) // 1024
        return {"total": total, "used": total - available}
    except Exception:
        return None


def _read_disk_space() -> list[dict]:
    """Read disk usage for key mount points."""
    disks = []
    for mount in ["/", "/vault", "/backup"]:
        try:
            usage = shutil.disk_usage(mount)
            disks.append({
                "mount": mount,
                "total_gb": round(usage.total / (1024**3), 1),
                "used_gb": round(usage.used / (1024**3), 1),
                "free_gb": round(usage.free / (1024**3), 1),
                "percent_used": round(usage.used / usage.total * 100, 1),
            })
        except FileNotFoundError:
            continue
    return disks


def _read_raid_status() -> str | None:
    """Check ZFS pool status or mdadm RAID status."""
    # Try ZFS first
    try:
        result = subprocess.run(
            ["zpool", "status", "-x"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try mdadm
    mdstat = Path("/proc/mdstat")
    if mdstat.exists():
        try:
            return mdstat.read_text().strip()
        except OSError:
            pass

    return None


def _read_battery() -> dict | None:
    """Read battery status from /sys/class/power_supply."""
    bat_path = Path("/sys/class/power_supply/BAT0")
    if not bat_path.exists():
        bat_path = Path("/sys/class/power_supply/battery")
    if not bat_path.exists():
        return None

    try:
        capacity = (bat_path / "capacity").read_text().strip()
        status = (bat_path / "status").read_text().strip()
        return {
            "percent": float(capacity),
            "charging": status.lower() in ("charging", "full"),
        }
    except (OSError, ValueError):
        return None


def _check_service(name: str) -> bool:
    """Check if a service is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", name],
            capture_output=True, timeout=3,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _read_uptime() -> float | None:
    """Read system uptime in seconds."""
    uptime_path = Path("/proc/uptime")
    if uptime_path.exists():
        try:
            return float(uptime_path.read_text().split()[0])
        except (ValueError, OSError):
            pass
    return None
