"""Offline map tile server for MBTiles files (OpenStreetMap data)."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class MBTilesReader:
    """Read map tiles from an MBTiles (SQLite) file."""

    def __init__(self, mbtiles_path: str | Path):
        self.path = Path(mbtiles_path)
        if not self.path.exists():
            raise FileNotFoundError(f"MBTiles file not found: {self.path}")
        self._conn = sqlite3.connect(str(self.path))

    def get_metadata(self) -> dict[str, str]:
        """Return the MBTiles metadata as a dictionary."""
        cursor = self._conn.execute("SELECT name, value FROM metadata")
        return dict(cursor.fetchall())

    def get_tile(self, z: int, x: int, y: int) -> bytes | None:
        """Fetch a single tile by zoom/x/y coordinates.

        MBTiles uses TMS y-coordinate (flipped), so we convert from
        standard slippy-map coordinates.
        """
        tms_y = (1 << z) - 1 - y
        cursor = self._conn.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
            (z, x, tms_y),
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_bounds(self) -> tuple[float, float, float, float] | None:
        """Return the bounding box (west, south, east, north) if available."""
        meta = self.get_metadata()
        bounds_str = meta.get("bounds")
        if bounds_str:
            parts = [float(p) for p in bounds_str.split(",")]
            if len(parts) == 4:
                return tuple(parts)
        return None

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def create_tile_app(mbtiles_path: str) -> "flask.Flask":
    """Create a Flask app that serves tiles from an MBTiles file.

    Serves tiles at: /tiles/{z}/{x}/{y}.pbf (or .png depending on format).
    Also serves a simple MapLibre GL JS viewer at /.
    """
    from flask import Flask, Response, abort

    app = Flask(__name__)
    reader = MBTilesReader(mbtiles_path)
    meta = reader.get_metadata()
    tile_format = meta.get("format", "pbf")

    content_types = {
        "pbf": "application/x-protobuf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "webp": "image/webp",
    }

    @app.route("/tiles/<int:z>/<int:x>/<int:y>")
    def serve_tile(z: int, x: int, y: int):
        tile_data = reader.get_tile(z, x, y)
        if tile_data is None:
            abort(404)
        content_type = content_types.get(tile_format, "application/octet-stream")
        headers = {}
        if tile_format == "pbf":
            headers["Content-Encoding"] = "gzip"
        return Response(tile_data, content_type=content_type, headers=headers)

    @app.route("/")
    def viewer():
        bounds = reader.get_bounds()
        center_lon = (bounds[0] + bounds[2]) / 2 if bounds else 0
        center_lat = (bounds[1] + bounds[3]) / 2 if bounds else 0
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>VaultMind Map</title>
    <script src="https://unpkg.com/maplibre-gl/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl/dist/maplibre-gl.css" rel="stylesheet" />
    <style>body {{ margin:0; }} #map {{ width:100%; height:100vh; }}</style>
</head>
<body>
    <div id="map"></div>
    <script>
        new maplibregl.Map({{
            container: 'map',
            style: {{
                version: 8,
                sources: {{
                    'local-tiles': {{
                        type: 'raster',
                        tiles: [window.location.origin + '/tiles/{{z}}/{{x}}/{{y}}'],
                        tileSize: 256
                    }}
                }},
                layers: [{{ id: 'tiles', type: 'raster', source: 'local-tiles' }}]
            }},
            center: [{center_lon}, {center_lat}],
            zoom: 10
        }});
    </script>
</body>
</html>"""

    return app
