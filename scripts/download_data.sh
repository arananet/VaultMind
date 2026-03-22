#!/usr/bin/env bash
# VaultMind Data Download Helper
# Run this script WHILE YOU STILL HAVE INTERNET to populate the vault.
set -euo pipefail

DATA_DIR="${1:-./data}"

echo "============================================"
echo "  VaultMind Data Downloader"
echo "  Preparing your offline knowledge vault..."
echo "============================================"
echo ""

# Create directories
mkdir -p "$DATA_DIR"/{pdfs,zim,tiles}

# --- PDFs ---
echo "[1/3] Downloading survival reference PDFs..."
echo "  Place your PDFs in: $DATA_DIR/pdfs/"
echo "  Recommended sources (download manually due to licensing):"
echo "    - 'Where There Is No Doctor' (Hesperian Health Guides)"
echo "    - 'US Army Survival Manual FM 21-76'"
echo "    - 'The Anarchist Cookbook' (chemistry reference)"
echo "    - 'Pocket Ref' by Thomas Glover"
echo ""

# --- Kiwix ZIM files ---
echo "[2/3] Downloading Kiwix .zim files..."
echo "  Download .zim files from: https://library.kiwix.org/"
echo "  Recommended:"
echo "    - wikipedia_en_all_nopic (text-only English Wikipedia, ~25GB)"
echo "    - stackexchange (survival, outdoors, DIY categories)"
echo "    - wikibooks_en_all (~1GB)"
echo ""
echo "  Place downloaded .zim files in: $DATA_DIR/zim/"
echo ""

# --- Map Tiles ---
echo "[3/3] Downloading offline map tiles..."
echo "  Generate MBTiles for your region using:"
echo "    https://openmaptiles.org/ or https://protomaps.com/"
echo "  For a 100km radius, expect 500MB-2GB depending on zoom levels."
echo ""
echo "  Place .mbtiles files in: $DATA_DIR/tiles/"
echo ""

# --- Pull Ollama model ---
echo "[+] Pulling LLM model via Ollama..."
if command -v ollama &>/dev/null; then
    ollama pull llama3.1:8b-instruct-q4_K_M
    echo "  Model downloaded successfully."
else
    echo "  Ollama not installed. Install from https://ollama.ai"
    echo "  Then run: ollama pull llama3.1:8b-instruct-q4_K_M"
fi

echo ""
echo "============================================"
echo "  Data preparation complete."
echo "  Next: vaultmind index --pdf-dir $DATA_DIR/pdfs"
echo "============================================"
