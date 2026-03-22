"""Tests for system monitor."""

from vaultmind.services.monitor import SystemStatus, get_system_status


def test_system_status_dataclass():
    """SystemStatus should initialize with sensible defaults."""
    status = SystemStatus()
    assert status.cpu_temp_c is None
    assert status.disks == []
    assert status.warnings == []
    assert status.ollama_running is False


def test_get_system_status_returns_status():
    """get_system_status should return a SystemStatus object."""
    status = get_system_status()
    assert isinstance(status, SystemStatus)
    assert isinstance(status.disks, list)
    assert isinstance(status.warnings, list)


def test_disk_space_includes_root():
    """Root filesystem should appear in disk check."""
    status = get_system_status()
    mounts = [d["mount"] for d in status.disks]
    assert "/" in mounts
