"""Maps.me-style offline maps integration for VaultMind.

Provides offline map tile serving from MBTiles files (OpenStreetMap data)
compatible with the Maps.me / Organic Maps approach to offline navigation.

Data sources:
  - MBTiles from OpenMapTiles: https://openmaptiles.org/
  - Protomaps basemaps:        https://protomaps.com/
  - Organic Maps .mwm regions: https://organicmaps.app/
"""

from __future__ import annotations

import logging
from pathlib import Path

from vaultmind.gis.tiles import MBTilesReader

logger = logging.getLogger(__name__)


class OfflineMapProvider:
    """Offline map provider using MBTiles as the tile backend.

    Wraps MBTilesReader and exposes map metadata and tile access
    through a single interface, mirroring the Maps.me offline-first model.
    """

    def __init__(self, mbtiles_path: str | Path):
        self.path = Path(mbtiles_path)
        self._reader = MBTilesReader(self.path)
        self._meta: dict[str, str] | None = None

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> dict[str, str]:
        if self._meta is None:
            self._meta = self._reader.get_metadata()
        return self._meta

    def get_info(self) -> dict:
        """Return structured map information for the API."""
        meta = self.metadata
        bounds = self._reader.get_bounds()
        center_lon, center_lat = 0.0, 0.0
        if bounds:
            center_lon = (bounds[0] + bounds[2]) / 2
            center_lat = (bounds[1] + bounds[3]) / 2

        min_zoom = int(meta.get("minzoom", 0))
        max_zoom = int(meta.get("maxzoom", 14))

        return {
            "name": meta.get("name", self.path.stem),
            "description": meta.get("description", "Offline map (OpenStreetMap)"),
            "format": meta.get("format", "pbf"),
            "attribution": meta.get("attribution", "© OpenStreetMap contributors"),
            "bounds": list(bounds) if bounds else None,
            "center": [center_lon, center_lat],
            "min_zoom": min_zoom,
            "max_zoom": max_zoom,
            "tile_url": "/api/map/tiles/{z}/{x}/{y}",
            "source": str(self.path.name),
        }

    # ------------------------------------------------------------------
    # Tile access
    # ------------------------------------------------------------------

    def get_tile(self, z: int, x: int, y: int) -> bytes | None:
        """Fetch a tile by zoom/x/y.  Returns None if not found."""
        return self._reader.get_tile(z, x, y)

    def get_tile_format(self) -> str:
        """Return the tile encoding format (pbf, png, jpg, webp)."""
        return self.metadata.get("format", "pbf")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._reader.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def get_provider(mbtiles_path: str | Path | None) -> OfflineMapProvider | None:
    """Return an OfflineMapProvider if an MBTiles file is configured and exists.

    Returns None (gracefully) if no file is configured or it doesn't exist.
    """
    if not mbtiles_path:
        return None
    path = Path(mbtiles_path)
    if not path.exists():
        logger.warning("MBTiles file not found: %s — offline maps unavailable", path)
        return None
    try:
        return OfflineMapProvider(path)
    except Exception as exc:
        logger.warning("Failed to open MBTiles %s: %s", path, exc)
        return None
