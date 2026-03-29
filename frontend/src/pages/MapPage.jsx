import { useEffect, useRef, useState } from "react";

const TILE_URL = "/api/map/tiles/{z}/{x}/{y}";

export default function MapPage() {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const [meta, setMeta] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch map metadata first
  useEffect(() => {
    fetch("/api/map/metadata")
      .then((r) => r.json())
      .then((data) => {
        if (!data.available) {
          setError(data.error || "Offline map not configured.");
        } else {
          setMeta(data);
        }
        setLoading(false);
      })
      .catch(() => {
        setError("Could not reach map API.");
        setLoading(false);
      });
  }, []);

  // Initialise MapLibre once metadata is available
  useEffect(() => {
    if (!meta || !mapRef.current || mapInstance.current) return;

    import("maplibre-gl").then(({ default: maplibregl }) => {
      const fmt = meta.format || "pbf";
      const isPbf = fmt === "pbf";

      const sourceConfig = isPbf
        ? {
            type: "vector",
            tiles: [window.location.origin + TILE_URL],
            minzoom: meta.min_zoom ?? 0,
            maxzoom: meta.max_zoom ?? 14,
            attribution: meta.attribution,
          }
        : {
            type: "raster",
            tiles: [window.location.origin + TILE_URL],
            tileSize: 256,
            minzoom: meta.min_zoom ?? 0,
            maxzoom: meta.max_zoom ?? 14,
            attribution: meta.attribution,
          };

      const style = isPbf
        ? {
            version: 8,
            sources: { "offline-tiles": sourceConfig },
            layers: [
              { id: "background", type: "background", paint: { "background-color": "#1a1a2e" } },
              {
                id: "tiles-fill",
                type: "fill",
                source: "offline-tiles",
                "source-layer": "landuse",
                paint: { "fill-color": "#16213e", "fill-opacity": 0.8 },
              },
              {
                id: "roads",
                type: "line",
                source: "offline-tiles",
                "source-layer": "transportation",
                paint: { "line-color": "#00e639", "line-width": 1 },
              },
              {
                id: "buildings",
                type: "fill",
                source: "offline-tiles",
                "source-layer": "building",
                paint: { "fill-color": "#0f3460", "fill-opacity": 0.7 },
              },
              {
                id: "water",
                type: "fill",
                source: "offline-tiles",
                "source-layer": "water",
                paint: { "fill-color": "#0d2137" },
              },
              {
                id: "place-labels",
                type: "symbol",
                source: "offline-tiles",
                "source-layer": "place",
                layout: { "text-field": ["get", "name"], "text-size": 12 },
                paint: { "text-color": "#e0e0e0", "text-halo-color": "#0a0a0a", "text-halo-width": 1 },
              },
            ],
          }
        : {
            version: 8,
            sources: { "offline-tiles": sourceConfig },
            layers: [{ id: "raster-tiles", type: "raster", source: "offline-tiles" }],
          };

      const map = new maplibregl.Map({
        container: mapRef.current,
        style,
        center: meta.center ?? [0, 0],
        zoom: 10,
      });

      map.addControl(new maplibregl.NavigationControl(), "top-right");
      map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
      map.addControl(
        new maplibregl.GeolocateControl({
          positionOptions: { enableHighAccuracy: true },
          trackUserLocation: true,
        }),
        "top-right"
      );

      mapInstance.current = map;
    });

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, [meta]);

  if (loading) {
    return (
      <div className="page-container">
        <div style={{ color: "var(--color-text-muted)", padding: "2rem" }}>
          Loading offline map...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <h2 style={{ color: "var(--color-accent)", marginBottom: "1rem" }}>
          Offline Maps
        </h2>
        <div
          style={{
            background: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: 8,
            padding: "1.5rem",
            maxWidth: 600,
          }}
        >
          <p style={{ color: "#ff6b6b", marginBottom: "1rem" }}>{error}</p>
          <p style={{ color: "var(--color-text-muted)", fontSize: "0.875rem", lineHeight: 1.6 }}>
            To enable offline maps, provide an MBTiles file and set{" "}
            <code>gis.mbtiles_path</code> in <code>config/vaultmind.yaml</code>{" "}
            or the <code>VAULTMIND_MBTILES_PATH</code> environment variable.
          </p>
          <p
            style={{
              color: "var(--color-text-muted)",
              fontSize: "0.875rem",
              lineHeight: 1.6,
              marginTop: "1rem",
            }}
          >
            Download MBTiles for your region from:
          </p>
          <ul
            style={{
              color: "var(--color-text-muted)",
              fontSize: "0.875rem",
              lineHeight: 1.8,
              paddingLeft: "1.25rem",
              marginTop: "0.5rem",
            }}
          >
            <li>Protomaps — protomaps.com (easiest, single-file downloads)</li>
            <li>OpenMapTiles — openmaptiles.org (full OpenStreetMap vector tiles)</li>
            <li>Organic Maps regions — organicmaps.app/downloads (country/region packs)</li>
          </ul>
          <p
            style={{
              color: "var(--color-text-muted)",
              fontSize: "0.875rem",
              marginTop: "1rem",
            }}
          >
            Run <code>scripts/download_data.sh</code> for guided setup.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container" style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "0.75rem",
          flexShrink: 0,
        }}
      >
        <h2 style={{ color: "var(--color-accent)", margin: 0 }}>Offline Maps</h2>
        <span
          style={{
            fontSize: "0.75rem",
            color: "var(--color-text-muted)",
            fontFamily: "var(--font-mono)",
          }}
        >
          {meta?.name} &middot; z{meta?.min_zoom}–{meta?.max_zoom} &middot;{" "}
          {meta?.format?.toUpperCase()}
        </span>
      </div>

      <div
        ref={mapRef}
        style={{
          flex: 1,
          minHeight: 0,
          borderRadius: 8,
          border: "1px solid var(--color-border)",
          overflow: "hidden",
        }}
      />

      <p
        style={{
          fontSize: "0.6875rem",
          color: "var(--color-text-muted)",
          marginTop: "0.5rem",
          flexShrink: 0,
        }}
      >
        {meta?.attribution}
      </p>
    </div>
  );
}
