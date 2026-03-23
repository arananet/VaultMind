"""Pre-flight diagnostics for all VaultMind services."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DiagnosticResult:
    """Result of a single diagnostic check."""

    name: str
    status: str  # "ok", "warn", "fail"
    message: str


def run_all_diagnostics(
    index_dir: str = "data/vault_index",
    guides_dir: str = "data/guides",
    pdf_dir: str = "data/pdfs",
    zim_dir: str = "data/zim",
    tiles_dir: str = "data/tiles",
    kiwix_url: str = "http://localhost:8888",
    model: str = "qwen3:8b",
) -> list[DiagnosticResult]:
    """Run all diagnostic checks and return results."""
    results = []

    # 1. Check Ollama
    results.append(_check_ollama(model))

    # 2. Check FAISS index
    results.append(_check_index(index_dir))

    # 3. Check knowledge guides
    results.append(_check_guides(guides_dir))

    # 4. Check PDFs
    results.append(_check_pdfs(pdf_dir))

    # 5. Check Kiwix
    results.append(_check_kiwix(kiwix_url))

    # 6. Check ZIM files
    results.append(_check_zim(zim_dir))

    # 7. Check map tiles
    results.append(_check_tiles(tiles_dir))

    # 8. Check disk space
    results.append(_check_disk_space())

    # 9. Check system health
    results.append(_check_system_health())

    return results


def _check_ollama(model: str) -> DiagnosticResult:
    """Check if Ollama is running and model is available."""
    try:
        import ollama as ollama_client

        models = ollama_client.list()
        model_names = [m.get("name", m.get("model", "")) for m in models.get("models", [])]
        if any(model in name for name in model_names):
            return DiagnosticResult("Ollama LLM", "ok", f"Model '{model}' available")
        return DiagnosticResult(
            "Ollama LLM", "warn",
            f"Ollama running but model '{model}' not found. "
            f"Available: {', '.join(model_names) or 'none'}",
        )
    except Exception as e:
        return DiagnosticResult("Ollama LLM", "fail", f"Ollama not reachable: {e}")


def _check_index(index_dir: str) -> DiagnosticResult:
    """Check if FAISS index exists."""
    path = Path(index_dir)
    if path.exists() and any(path.iterdir()):
        size_mb = sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / (1024 * 1024)
        return DiagnosticResult("FAISS Index", "ok", f"Index loaded ({size_mb:.1f} MB)")
    return DiagnosticResult(
        "FAISS Index", "warn",
        "No index found. Run 'vaultmind index' to build it.",
    )


def _check_guides(guides_dir: str) -> DiagnosticResult:
    """Check bundled knowledge guides."""
    path = Path(guides_dir)
    if not path.is_dir():
        return DiagnosticResult("Knowledge Guides", "fail", f"Guides directory not found: {guides_dir}")

    md_files = list(path.rglob("*.md"))
    domains = {f.parent.name for f in md_files}
    if md_files:
        return DiagnosticResult(
            "Knowledge Guides", "ok",
            f"{len(md_files)} guides across {len(domains)} domains: {', '.join(sorted(domains))}",
        )
    return DiagnosticResult("Knowledge Guides", "warn", "No guide files found")


def _check_pdfs(pdf_dir: str) -> DiagnosticResult:
    """Check PDF library."""
    path = Path(pdf_dir)
    if not path.is_dir():
        return DiagnosticResult("PDF Library", "warn", "PDF directory not found")

    pdfs = list(path.glob("*.pdf"))
    if pdfs:
        total_mb = sum(f.stat().st_size for f in pdfs) / (1024 * 1024)
        return DiagnosticResult("PDF Library", "ok", f"{len(pdfs)} PDFs ({total_mb:.0f} MB)")
    return DiagnosticResult("PDF Library", "warn", "No PDFs found. Add survival manuals to data/pdfs/")


def _check_kiwix(kiwix_url: str) -> DiagnosticResult:
    """Check Kiwix server availability."""
    try:
        import requests

        resp = requests.get(f"{kiwix_url}/", timeout=2)
        if resp.status_code == 200:
            return DiagnosticResult("Kiwix Server", "ok", f"Running at {kiwix_url}")
    except Exception:
        pass
    return DiagnosticResult(
        "Kiwix Server", "warn",
        f"Not reachable at {kiwix_url}. Start with: kiwix-serve --port 8888 data/zim/*.zim",
    )


def _check_zim(zim_dir: str) -> DiagnosticResult:
    """Check for .zim archives."""
    path = Path(zim_dir)
    if not path.is_dir():
        return DiagnosticResult("ZIM Archives", "warn", "ZIM directory not found")

    zims = list(path.glob("*.zim"))
    if zims:
        total_gb = sum(f.stat().st_size for f in zims) / (1024**3)
        return DiagnosticResult("ZIM Archives", "ok", f"{len(zims)} archives ({total_gb:.1f} GB)")
    return DiagnosticResult(
        "ZIM Archives", "warn",
        "No .zim files found. Download from https://library.kiwix.org/",
    )


def _check_tiles(tiles_dir: str) -> DiagnosticResult:
    """Check for MBTiles map files."""
    path = Path(tiles_dir)
    if not path.is_dir():
        return DiagnosticResult("Map Tiles", "warn", "Tiles directory not found")

    tiles = list(path.glob("*.mbtiles"))
    if tiles:
        total_gb = sum(f.stat().st_size for f in tiles) / (1024**3)
        return DiagnosticResult("Map Tiles", "ok", f"{len(tiles)} tile files ({total_gb:.1f} GB)")
    return DiagnosticResult("Map Tiles", "warn", "No MBTiles files found for offline maps")


def _check_disk_space() -> DiagnosticResult:
    """Check available disk space."""
    import shutil

    try:
        usage = shutil.disk_usage("/")
        free_gb = usage.free / (1024**3)
        pct = usage.used / usage.total * 100
        if free_gb < 5:
            return DiagnosticResult(
                "Disk Space", "warn",
                f"Low disk space: {free_gb:.1f} GB free ({pct:.0f}% used)",
            )
        return DiagnosticResult(
            "Disk Space", "ok",
            f"{free_gb:.1f} GB free ({pct:.0f}% used)",
        )
    except Exception as e:
        return DiagnosticResult("Disk Space", "fail", f"Cannot read disk space: {e}")


def _check_system_health() -> DiagnosticResult:
    """Check overall system health."""
    from vaultmind.services.monitor import get_system_status

    status = get_system_status()
    if status.warnings:
        return DiagnosticResult(
            "System Health", "warn",
            "; ".join(status.warnings),
        )
    parts = []
    if status.cpu_temp_c:
        parts.append(f"CPU: {status.cpu_temp_c}°C")
    if status.memory_total_mb and status.memory_used_mb:
        parts.append(f"RAM: {status.memory_used_mb}/{status.memory_total_mb} MB")
    if status.uptime_seconds:
        hours = status.uptime_seconds / 3600
        parts.append(f"Uptime: {hours:.1f}h")
    return DiagnosticResult(
        "System Health", "ok",
        "; ".join(parts) if parts else "System healthy",
    )
