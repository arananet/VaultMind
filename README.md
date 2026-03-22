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
| Logic     | Ollama / Llama.cpp     | Llama 3.1 8B (Quantized to Q4_K_M for speed)                      |
| Search    | Kiwix                  | `.zim` files (Wikipedia, StackExchange, Project Gutenberg)         |
| Space     | MapLibre / MBTiles     | OpenStreetMap (Local MBTiles for your 100km radius)                |
| Vitals    | RAG Engine             | PDF library + bundled survival knowledge guides                    |
| Comms     | Meshtastic Integration | Local LoRa node monitoring for off-grid messaging                  |
| Monitor   | System Monitor         | CPU temp, disk health, battery, RAID status                        |

---

## Bundled Knowledge Guides

VaultMind ships with structured survival guides across 10 critical domains,
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

---

## Recommended Base Hardware

### Primary Node — "The Vault"

| Component        | Recommended                      | Budget Alternative              |
|------------------|----------------------------------|---------------------------------|
| **Computer**     | Intel N100 Mini PC (16GB RAM)    | Raspberry Pi 5 (8GB)           |
| **Storage**      | 2x 2TB NVMe SSD (ZFS mirror)    | 2x 1TB SATA SSD (mdadm RAID1) |
| **Cold Backup**  | 1x 4TB USB HDD                  | 1x 2TB USB HDD                |
| **Battery**      | 12V 200Ah LiFePO4               | 12V 100Ah AGM                  |
| **Solar Panel**  | 200W monocrystalline             | 100W portable panel            |
| **Charge Ctrl**  | Victron SmartSolar MPPT 75/15    | EPever Tracer 10A MPPT         |
| **UPS**          | 12V DC mini-UPS board            | Manual switchover              |
| **Radio**        | Heltec V3 LoRa (Meshtastic)     | TTGO T-Beam                    |
| **Enclosure**    | Pelican 1550 (waterproof)        | Ammo can + foam                |

**Power Budget:** N100 draws ~15-25W. With 200Ah LiFePO4 + 200W solar panel,
the system runs indefinitely with 5+ sun-hours/day, or 4-7 days without solar.

### Mobile Node — "The Satchel"

| Component     | Recommended                 | Notes                          |
|---------------|-----------------------------|---------------------------------|
| **Computer**  | Raspberry Pi 5 (8GB)        | Runs Phi-3 Mini at ~5 tok/s    |
| **Storage**   | 1TB microSD + 1TB USB SSD   | microSD for OS, SSD for data   |
| **Power**     | 100Wh USB-C power bank      | ~12 hours runtime              |
| **Solar**     | 28W foldable USB-C panel    | Trickle charge in the field    |
| **Radio**     | Heltec V3 LoRa              | Mesh link back to base vault   |
| **Case**      | Pelican 1200 micro          | Fits in a backpack             |

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

### Download a Model

```bash
ollama pull llama3.1:8b-instruct-q4_K_M
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
│   └── services/              # Guide indexer, system monitor, diagnostics
├── data/
│   ├── guides/                # 10 survival domain knowledge guides
│   │   ├── medicine/          # Field medicine, antibiotics, pain management
│   │   ├── chemistry/         # Soap, disinfectants, activated charcoal
│   │   ├── energy/            # Gasification, biodiesel, ethanol, solar
│   │   ├── agriculture/       # Farming, foraging, animal husbandry
│   │   ├── water/             # Purification, wells, rainwater harvesting
│   │   ├── construction/      # Shelter, concrete, plumbing, electrical
│   │   ├── communications/    # HAM radio, antennas, Morse code
│   │   ├── metalworking/      # Forge, blacksmithing, vehicle repair
│   │   ├── navigation/        # Celestial nav, compass, dead reckoning
│   │   └── security/          # Perimeter defense, community, OPSEC
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
