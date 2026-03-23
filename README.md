# VaultMind

**"Knowledge is the only resource that doesn't deplete when shared."**

VaultMind is a decentralized, air-gapped knowledge appliance designed for
high-availability intelligence in "Scenario Zero" environments. It merges
local LLM reasoning with a massive static library (Wikipedia, WikiHow,
Medical Manuals) and offline GIS, ensuring that even if the internet ceases
to exist, the sum of human ingenuity remains accessible from a single device.

> See [SPEC.md](SPEC.md) for the full system specification.
> See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## Architecture: The Survival Stack

| Layer     | Service                | Data Source                                                        |
|-----------|------------------------|--------------------------------------------------------------------|
| Logic     | Ollama / Llama.cpp     | Qwen3 8B (Q4_K_M, 5.2GB) — verified Ollama tag                   |
| Search    | Kiwix                  | `.zim` files (Wikipedia, StackExchange, Project Gutenberg)         |
| Space     | MapLibre / MBTiles     | OpenStreetMap (Local MBTiles for your 100km radius)                |
| Vitals    | RAG Engine             | PDF library + bundled survival knowledge guides                    |
| Comms     | Meshtastic Integration | Local LoRa node monitoring for off-grid messaging                  |
| Monitor   | System Monitor         | CPU temp, disk health, battery, RAID status                        |
| Voice     | Piper / Chatterbox TTS | Offline text-to-speech (CPU or GPU)                                |
| Database  | PostgreSQL / SQLite    | Query logs, sensor data, automation rules, TTS cache               |
| Hardware  | gpiod / I2C / USB      | GPIO control, sensor reading, relay automation                     |

---

## Bundled Knowledge Guides

VaultMind ships with structured survival guides across 11 critical domains,
all indexed into the RAG pipeline for instant retrieval:

| Domain                  | Key Topics                                                              |
|-------------------------|-------------------------------------------------------------------------|
| **Field Medicine**      | Wound care, suturing, antibiotics cultivation (penicillin), pain relief |
|                         | (willow bark aspirin), dental emergencies, emergency childbirth         |
| **Chemistry & Pharmacy**| Soap making (from ash lye), disinfectant production, activated charcoal,|
|                         | water treatment chemicals, vinegar production, food preservatives       |
| **Energy & Fuel**       | Wood gasification (syngas for engines), biodiesel from vegetable oil,   |
|                         | ethanol distillation, methanol from wood, solar panel maintenance,      |
|                         | generator repair, battery recovery                                      |
| **Agriculture**         | Seed saving, crop rotation, composting, soil building, animal husbandry |
|                         | (chickens, rabbits, goats), wild edible identification, food preservation|
| **Water Systems**       | Boiling, solar distillation, bio-sand filters, chlorination, iodine,    |
|                         | rainwater harvesting, manual well drilling, field water testing          |
| **Construction**        | Debris huts, wattle-and-daub, rammed earth, lime mortar, Roman concrete,|
|                         | plumbing, electrical wiring, composting toilets, sanitation              |
| **Communications**      | HAM radio frequencies, antenna building (dipole, ground plane),          |
|                         | Morse code, Meshtastic LoRa mesh, signal propagation                    |
| **Metalworking**        | Charcoal forge building, blacksmithing, knife making, brazing/soldering,|
|                         | tool fabrication, vehicle repair diagnostics                             |
| **Navigation**          | Compass/map reading, celestial navigation (Polaris, Southern Cross),     |
|                         | dead reckoning, pace counting, terrain association                       |
| **Security**            | Community organization, perimeter defense, watch protocols,              |
|                         | conflict de-escalation, OPSEC, barter/trade, mental health               |
| **International Radio** | ITU regions, international HF band plan, distress frequencies,          |
|                         | emergency nets (IARN, SATERN), NATO phonetic, Q-codes, digital modes     |

---

## Recommended Base Hardware

VaultMind supports 4 hardware tiers. See [SPEC.md](SPEC.md) for full details.

| Tier | Name           | Computer                  | Max Model                     | Power Draw  |
|------|----------------|---------------------------|-------------------------------|-------------|
| 1    | "The Satchel"  | Raspberry Pi 5 (8GB)      | `qwen3:0.6b` (523MB)         | ~8W         |
| 2    | "The Vault"    | Intel N100 Mini PC (16GB) | `qwen3:8b` (5.2GB)           | ~15-25W     |
| 3    | "The Forge"    | Mini-ITX + RTX 4060 Ti    | `phi4-reasoning` (14B, 11GB) | ~65-220W    |
| 4    | "The Citadel"  | Workstation + RTX 4090    | `qwen3:30b` (19GB)           | ~150-450W   |

**Tier 3 is the minimum for reasoning models.** The RTX 4060 Ti 16GB runs
`phi4-reasoning` (14B) natively and outperforms many 70B models on structured
reasoning tasks.

### Storage Redundancy Strategy

```
ZFS Mirror Pool (2x NVMe)     ← Real-time redundancy (survives 1 drive failure)
    ├── Hourly ZFS snapshots   ← Rollback on corruption (7 days retained)
    └── Monthly zfs send/recv  ← Cold backup to USB HDD (stored separately)
```

ZFS provides **self-healing checksums** on every read — if a bit flips on one
drive, ZFS automatically repairs it from the mirror. This is critical for
long-term data integrity without internet access to re-download anything.

---

## Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed locally
- (Optional) Kiwix server for `.zim` file search
- (Optional) MBTiles files for offline map support

### Installation

```bash
pip install -e .
```

### Download Models

```bash
ollama pull qwen3:8b              # Primary (5.2GB)
ollama pull qwen3:4b              # Lightweight (2.5GB)
ollama pull phi4-reasoning         # Reasoning (11GB, optional, needs GPU)
```

### Download Data (While You Still Have Internet)

```bash
./scripts/download_data.sh
```

### Index Your Knowledge Vault

```bash
# Index bundled guides + your PDFs
vaultmind index --pdf-dir ./data/pdfs --include-guides

# Or guides only (no PDFs yet)
vaultmind index --include-guides
```

### Query VaultMind

```bash
# Single query
vaultmind query "How do I make biodiesel from cooking oil?"

# Interactive chat
vaultmind chat

# Web interface
vaultmind serve --port 8080
```

### System Diagnostics

```bash
vaultmind diagnostics
```

---

## Docker Deployment

```bash
docker compose up -d
```

This starts VaultMind + Ollama + Kiwix. Place your data files:
- PDFs → `data/pdfs/`
- ZIM archives → `data/zim/`
- MBTiles → `data/tiles/`

---

## Project Structure

```
VaultMind/
├── SPEC.md                    # Full system specification
├── CHANGELOG.md               # Version history
├── vaultmind/
│   ├── core/                  # Query router, S.T.A.R. prompt engine
│   ├── rag/                   # PDF ingestion, FAISS vector store, retrieval
│   ├── search/                # Kiwix .zim file search integration
│   ├── gis/                   # Offline map tile serving (MBTiles/MapLibre)
│   ├── comms/                 # Meshtastic LoRa integration
│   ├── services/              # Guide indexer, system monitor, diagnostics
│   ├── web/                   # Flask app factory + REST API blueprint
│   ├── db/                    # PostgreSQL/SQLite ORM, migrations, schema docs
│   ├── tts/                   # Offline TTS (Piper, Chatterbox, Kokoro, espeak)
│   └── hardware/              # GPIO, I2C sensors, USB relays, automation engine
├── frontend/                  # React 19 + Vite UI (builds to vaultmind/static/)
├── alembic/                   # Database migration versions
├── data/
│   ├── guides/                # 11 survival domain knowledge guides
│   │   ├── medicine/          # Field medicine, antibiotics, pain management
│   │   ├── chemistry/         # Soap, disinfectants, activated charcoal
│   │   ├── energy/            # Gasification, biodiesel, ethanol, solar
│   │   ├── agriculture/       # Farming, foraging, animal husbandry
│   │   ├── water/             # Purification, wells, rainwater harvesting
│   │   ├── construction/      # Shelter, concrete, plumbing, electrical
│   │   ├── communications/    # HAM radio, antennas, Morse code
│   │   ├── metalworking/      # Forge, blacksmithing, vehicle repair
│   │   ├── navigation/        # Celestial nav, compass, dead reckoning
│   │   ├── security/          # Perimeter defense, community, OPSEC
│   │   └── radio_international/ # ITU regions, HF bands, emergency nets
│   ├── pdfs/                  # Your survival manuals (user-provided)
│   ├── zim/                   # Kiwix .zim archives
│   └── tiles/                 # MBTiles map files
├── config/                    # Configuration (vaultmind.yaml)
├── scripts/                   # Setup and data download helpers
└── tests/                     # Test suite
```

---

## Recommended PDF Library

Download these **before the grid goes down**:

### Medical
- Where There Is No Doctor (Hesperian Health Guides)
- Where There Is No Dentist (Hesperian Health Guides)
- Emergency War Surgery (NATO/Borden Institute)
- Tactical Combat Casualty Care Handbook

### Survival & Field Craft
- US Army Survival Manual (FM 21-76 / FM 3-05.70)
- SAS Survival Handbook (John Wiseman)
- US Army Ranger Handbook (SH 21-76)

### Engineering
- Pocket Ref (Thomas Glover)
- Machinery's Handbook
- The Humanure Handbook

### Agriculture
- The New Self-Sufficient Gardener (John Seymour)
- Seed to Seed (Suzanne Ashworth)
- Ball Complete Book of Home Preserving

### Energy & Science
- The Knowledge: How to Rebuild Civilization (Lewis Dartnell)
- Practical Electronics for Inventors
- Solar Electricity Handbook
- ARRL Handbook for Radio Communications

---

## License

MIT

## Author

Eduardo Arana
