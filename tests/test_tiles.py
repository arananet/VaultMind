"""Tests for MBTiles reader."""

import sqlite3
from pathlib import Path

import pytest

from vaultmind.gis.tiles import MBTilesReader


def test_mbtiles_file_not_found():
    with pytest.raises(FileNotFoundError):
        MBTilesReader("/nonexistent/file.mbtiles")


def test_mbtiles_reader(tmp_path):
    """Test reading from a minimal MBTiles file."""
    db_path = tmp_path / "test.mbtiles"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE metadata (name TEXT, value TEXT)"
    )
    conn.execute(
        "INSERT INTO metadata VALUES ('name', 'test'), ('format', 'png'), ('bounds', '-1,-1,1,1')"
    )
    conn.execute(
        "CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB)"
    )
    conn.execute(
        "INSERT INTO tiles VALUES (0, 0, 0, X'89504E47')"  # PNG magic bytes
    )
    conn.commit()
    conn.close()

    reader = MBTilesReader(db_path)
    meta = reader.get_metadata()
    assert meta["name"] == "test"
    assert meta["format"] == "png"

    bounds = reader.get_bounds()
    assert bounds == (-1.0, -1.0, 1.0, 1.0)

    # z=0, x=0, y=0 -> TMS y = 0
    tile = reader.get_tile(0, 0, 0)
    assert tile is not None

    # Non-existent tile
    assert reader.get_tile(5, 5, 5) is None

    reader.close()
