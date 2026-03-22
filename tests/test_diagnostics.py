"""Tests for diagnostic checks."""

from vaultmind.services.diagnostics import DiagnosticResult, run_all_diagnostics


def test_diagnostic_result_dataclass():
    """DiagnosticResult should hold name, status, and message."""
    result = DiagnosticResult(name="Test", status="ok", message="All good")
    assert result.name == "Test"
    assert result.status == "ok"
    assert result.message == "All good"


def test_run_all_diagnostics_returns_results():
    """run_all_diagnostics should return a list of results."""
    results = run_all_diagnostics()
    assert isinstance(results, list)
    assert len(results) >= 5  # Should have multiple checks
    for r in results:
        assert isinstance(r, DiagnosticResult)
        assert r.status in ("ok", "warn", "fail")
        assert r.name
        assert r.message


def test_diagnostics_includes_key_services():
    """Diagnostics should check all critical services."""
    results = run_all_diagnostics()
    names = {r.name for r in results}
    assert "Knowledge Guides" in names
    assert "Disk Space" in names
    assert "System Health" in names
