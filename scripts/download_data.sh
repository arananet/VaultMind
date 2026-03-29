#!/usr/bin/env bash
# VaultMind Data Download Helper
# =============================================================================
# Run this script WHILE YOU STILL HAVE INTERNET to populate the vault.
# This is your last chance to download the sum of human knowledge.
# =============================================================================
set -euo pipefail

DATA_DIR="${1:-./data}"

echo "============================================================"
echo "  VaultMind Data Downloader"
echo "  Preparing your offline knowledge vault..."
echo "  'Knowledge is the only resource that doesn't deplete when shared.'"
echo "============================================================"
echo ""

# Create directories
mkdir -p "$DATA_DIR"/{pdfs,zim,tiles,guides,tts_cache}

# ============================================================================
# [1/5] PDF Reference Library
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1/5] PDF Reference Library"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Place PDFs in: $DATA_DIR/pdfs/"
echo ""
echo "  MEDICAL (Critical):"
echo "    - Where There Is No Doctor (Hesperian Health Guides)"
echo "    - Where There Is No Dentist (Hesperian Health Guides)"
echo "    - Emergency War Surgery (NATO/Borden Institute)"
echo "    - Tactical Combat Casualty Care Handbook"
echo "    - WHO Essential Medicines List"
echo ""
echo "  SURVIVAL & FIELD CRAFT:"
echo "    - US Army Survival Manual (FM 21-76 / FM 3-05.70)"
echo "    - SAS Survival Handbook (John Wiseman)"
echo "    - US Army Ranger Handbook (SH 21-76)"
echo "    - Bushcraft 101 (Dave Canterbury)"
echo ""
echo "  ENGINEERING & SCIENCE:"
echo "    - Pocket Ref (Thomas Glover)"
echo "    - Machinery's Handbook"
echo "    - The Knowledge: How to Rebuild Civilization (Lewis Dartnell)"
echo "    - Practical Electronics for Inventors"
echo "    - Chemistry: The Central Science"
echo ""
echo "  AGRICULTURE & FOOD:"
echo "    - The New Self-Sufficient Gardener (John Seymour)"
echo "    - Seed to Seed (Suzanne Ashworth)"
echo "    - Ball Complete Book of Home Preserving"
echo "    - Storey's Guides (Chickens, Goats, Rabbits)"
echo ""
echo "  ENERGY & POWER:"
echo "    - Solar Electricity Handbook"
echo "    - The Humanure Handbook"
echo ""
echo "  COMMUNICATIONS:"
echo "    - ARRL Handbook for Radio Communications"
echo "    - The ARRL Antenna Book"
echo ""

# ============================================================================
# [2/5] Kiwix ZIM Archives
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[2/5] Kiwix ZIM Archives"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Download .zim files from: https://library.kiwix.org/"
echo "  Place in: $DATA_DIR/zim/"
echo ""
echo "  RECOMMENDED (Total ~50GB):"
echo "    - wikipedia_en_all_nopic    (~25GB)  Full English Wikipedia"
echo "    - wikibooks_en_all          (~1GB)   Textbooks and how-tos"
echo "    - wikihow_en_all            (~3GB)   Step-by-step guides"
echo "    - stackexchange_combined    (~10GB)  Q&A (survival, DIY, cooking)"
echo "    - gutenberg_en_all          (~8GB)   60,000+ public domain books"
echo "    - wikiversity_en_all        (~500MB) Educational courses"
echo ""
echo "  MINIMAL SET (~30GB):"
echo "    - wikipedia_en_all_nopic    (~25GB)"
echo "    - wikihow_en_all            (~3GB)"
echo "    - wikibooks_en_all          (~1GB)"
echo ""

# ============================================================================
# [3/5] Offline Map Tiles (Maps.me / Organic Maps compatible)
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[3/5] Offline Map Tiles (Maps.me / Organic Maps)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  VaultMind serves offline maps from MBTiles files via MapLibre GL."
echo "  Compatible with the same OpenStreetMap data used by Maps.me /"
echo "  Organic Maps — works fully offline with no external tile server."
echo ""
echo "  OPTION A — Protomaps (easiest, single-file vector tiles):"
echo "    1. Visit https://protomaps.com/builds"
echo "    2. Select your region and download the .pmtiles file"
echo "    3. Convert to MBTiles:"
echo "         pmtiles convert region.pmtiles region.mbtiles"
echo "    4. Rename to local.mbtiles and place in $DATA_DIR/tiles/"
echo ""
echo "  OPTION B — OpenMapTiles (full OpenStreetMap vector tiles):"
echo "    1. Visit https://openmaptiles.org/downloads/"
echo "    2. Download the .mbtiles file for your country/region"
echo "    3. Place in $DATA_DIR/tiles/  (rename to local.mbtiles or keep as-is)"
echo ""
echo "  OPTION C — Organic Maps region packs (offline navigation data):"
echo "    1. Visit https://organicmaps.app/ to learn about .mwm format"
echo "    2. Use bbf/osmand-map-creator to export regions as MBTiles"
echo "    3. Place resulting .mbtiles in $DATA_DIR/tiles/"
echo ""
echo "  OPTION D — Custom region via osmium + tippecanoe:"
echo "    # Download OSM extract from https://download.geofabrik.de/"
echo "    osmium extract --bbox=WEST,SOUTH,EAST,NORTH region.osm.pbf -o local.osm.pbf"
echo "    tippecanoe -o $DATA_DIR/tiles/local.mbtiles -z14 local.geojson"
echo ""
echo "  Recommendations:"
echo "    - Zoom levels 0-14 (overview to detailed street level)"
echo "    - 100km radius around your location for daily use"
echo "    - Expected size: 500MB-3GB per region (vector PBF tiles)"
echo ""
echo "  After placing the file, update config/vaultmind.yaml:"
echo "    gis:"
echo "      enabled: true"
echo "      mbtiles_path: \"$DATA_DIR/tiles/local.mbtiles\""
echo ""
echo "  Tile viewer: http://localhost:8080/map  (after vaultmind serve)"
echo "  Tile API:    http://localhost:8080/api/map/tiles/{z}/{x}/{y}"
echo ""

# ============================================================================
# [4/5] LLM Models via Ollama
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[4/5] Pulling LLM Models via Ollama"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
if command -v ollama &>/dev/null; then
    echo "  Ollama detected. Pulling models..."
    echo ""

    echo "  [Primary] Qwen3 8B (Q4_K_M default, ~5.2GB)..."
    ollama pull qwen3:8b || echo "    WARN: Failed to pull primary model"

    echo "  [Lightweight] Qwen3 4B (Q4_K_M, ~2.5GB, 256K context)..."
    ollama pull qwen3:4b || echo "    WARN: Failed to pull lightweight model"

    echo "  [Tiny/Edge] Qwen3 0.6B (~523MB)..."
    ollama pull qwen3:0.6b || echo "    WARN: Failed to pull tiny model"

    echo ""
    echo "  Optional reasoning models (requires more VRAM/RAM):"
    echo "  [Reasoning] Phi4-Reasoning 14B (~11GB, needs 16GB+ RAM)..."
    ollama pull phi4-reasoning || echo "    WARN: Failed to pull reasoning model"

    echo "  [Edge Reasoning] Phi4-Mini-Reasoning 3.8B (~3.2GB)..."
    ollama pull phi4-mini-reasoning || echo "    WARN: Failed to pull edge reasoning model"

    echo ""
    echo "  Models downloaded successfully."
else
    echo "  Ollama not installed."
    echo "  Install from https://ollama.ai then run:"
    echo "    ollama pull qwen3:8b              # Primary (5.2GB)"
    echo "    ollama pull qwen3:4b              # Lightweight (2.5GB)"
    echo "    ollama pull qwen3:0.6b            # Tiny edge (523MB)"
    echo "    ollama pull phi4-reasoning         # Reasoning (11GB, optional)"
    echo "    ollama pull phi4-mini-reasoning    # Edge reasoning (3.2GB, optional)"
fi
echo ""

# ============================================================================
# [5/5] Embedding Model
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[5/5] Pre-downloading Embedding Model"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
if command -v python3 &>/dev/null; then
    echo "  Downloading sentence-transformers/all-MiniLM-L6-v2..."
    python3 -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print('  Embedding model cached successfully.')
" 2>/dev/null || echo "  WARN: Could not pre-download embedding model. It will download on first index."
else
    echo "  Python3 not found. Embedding model will download on first 'vaultmind index' run."
fi
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "============================================================"
echo "  Data preparation complete."
echo ""
echo "  Next steps:"
echo "    1. Add your PDFs to $DATA_DIR/pdfs/"
echo "    2. Download .zim files to $DATA_DIR/zim/"
echo "    3. Generate MBTiles to $DATA_DIR/tiles/"
echo "    4. Build the index:"
echo "       vaultmind index --pdf-dir $DATA_DIR/pdfs --include-guides"
echo "    5. Run diagnostics:"
echo "       vaultmind diagnostics"
echo "    6. Start VaultMind:"
echo "       vaultmind serve --port 8080"
echo ""
echo "  After deployment, disconnect from the internet."
echo "  You are now air-gapped. The vault is sealed."
echo "============================================================"
