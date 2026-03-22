# VaultMind

**"Knowledge is the only resource that doesn't deplete when shared."**

VaultMind is a decentralized, air-gapped knowledge appliance designed for high-availability intelligence in "Scenario Zero" environments. It merges local LLM reasoning with a massive static library (Wikipedia, WikiHow, Medical Manuals) and offline GIS, ensuring that even if the internet ceases to exist, the sum of human ingenuity remains accessible.

## Architecture: The Survival Stack

| Layer   | Service                | Data Source                                                        |
|---------|------------------------|--------------------------------------------------------------------|
| Logic   | Ollama / Llama.cpp     | Llama 3.1 8B (Quantized to Q4_K_M for speed)                      |
| Search  | Kiwix                  | `.zim` files (Wikipedia, StackExchange, Project Gutenberg)         |
| Space   | MapLibre / Tiles       | OpenStreetMap (Local MBTiles for your 100km radius)                |
| Vitals  | RAG Engine             | PDF library (Where There Is No Doctor, US Army Survival Manual)    |
| Comms   | Meshtastic Integration | Local LoRa node monitoring for off-grid messaging                  |

## Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) installed and running locally
- (Optional) Kiwix server for `.zim` file search
- (Optional) MBTiles files for offline map support

### Installation

```bash
pip install -e .
```

### Download a Model

```bash
ollama pull llama3.1:8b-instruct-q4_K_M
```

### Index Your PDF Library

```bash
vaultmind index --pdf-dir ./data/pdfs
```

### Launch VaultMind

```bash
vaultmind query "How do I purify water using basic materials?"
```

### Start the Web Interface

```bash
vaultmind serve --port 8080
```

## Project Structure

```
VaultMind/
├── vaultmind/
│   ├── core/          # Unified query router and S.T.A.R. prompt engine
│   ├── rag/           # PDF ingestion, chunking, vector store, retrieval
│   ├── search/        # Kiwix .zim file search integration
│   ├── gis/           # Offline map tile serving (MBTiles/MapLibre)
│   └── comms/         # Meshtastic LoRa integration
├── data/
│   ├── pdfs/          # Survival manuals, medical references
│   ├── zim/           # Kiwix .zim archives
│   └── tiles/         # MBTiles map files
├── config/            # Configuration files
├── scripts/           # Setup and data download helpers
└── tests/             # Test suite
```

## The Protocol Zero System Prompt

VaultMind uses the **S.T.A.R.** method for all responses:

- **Situation**: Identify the immediate danger
- **Tools**: List required items (low-tech focus)
- **Action**: Step-by-step, numbered instructions
- **Risk**: Warning labels for what could go wrong

When data is not found in the local vault, VaultMind responds with:
> "Data Not Found in Vault."

No hallucinations. In a survival scenario, a wrong answer is fatal.

## License

MIT

## Author

Eduardo Arana
