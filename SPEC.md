# VaultMind System Specification

**Version:** 0.2.0
**Status:** Active Development
**Author:** Eduardo Arana
**Last Updated:** 2026-03-22

---

## 1. Mission Statement

VaultMind is a decentralized, air-gapped knowledge appliance designed for
high-availability intelligence in "Scenario Zero" environments. When the
internet ceases to exist, VaultMind ensures the sum of human ingenuity
remains accessible from a single device.

**Design Principles:**
- Zero external connectivity required after initial provisioning
- No hallucinations: wrong answers kill in survival scenarios
- Low-power operation: must run on battery/solar indefinitely
- Redundant storage: no single disk failure loses the vault
- Modular services: each layer operates independently

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        VaultMind Shell                          │
│                   (CLI / Web UI / API)                          │
├────────────┬────────────┬──────────┬──────────┬────────────────┤
│  Query     │  Knowledge │  Offline │  Mesh    │  System        │
│  Router    │  Guides    │  GIS     │  Comms   │  Monitor       │
├────────────┼────────────┼──────────┼──────────┼────────────────┤
│  RAG       │  Kiwix     │  MBTiles │  LoRa    │  Power/HW      │
│  Engine    │  Search    │  Server  │  Bridge  │  Manager       │
├────────────┴────────────┴──────────┴──────────┴────────────────┤
│                    Local LLM (Ollama)                           │
├────────────────────────────────────────────────────────────────┤
│                    FAISS Vector Store                           │
├────────────────────────────────────────────────────────────────┤
│               Redundant Storage (ZFS/Btrfs RAID)               │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Service Layers

### 3.1 Logic Layer — Local LLM

| Property        | Value                                      |
|-----------------|--------------------------------------------|
| Runtime         | Ollama / llama.cpp                         |
| Primary Model   | Llama 3.1 8B Instruct (Q4_K_M, ~4.7GB)    |
| Fallback Model  | Mistral 7B Instruct (Q4_K_M, ~4.1GB)      |
| Tiny Model      | Phi-3 Mini 3.8B (Q4_K_M, ~2.2GB)          |
| Embedding Model | all-MiniLM-L6-v2 (sentence-transformers)   |
| Device          | CPU (ARM64/x86_64), optional GPU           |
| Response Method | S.T.A.R. (Situation, Tools, Action, Risk)  |

### 3.2 RAG Layer — PDF Knowledge Vault

| Property        | Value                                      |
|-----------------|--------------------------------------------|
| Ingestion       | PyMuPDF (PDF → text extraction)            |
| Chunking        | RecursiveCharacterTextSplitter (1000/200)  |
| Embeddings      | HuggingFace sentence-transformers          |
| Vector Store    | FAISS (CPU, persisted to disk)             |
| Retrieval       | Top-k similarity search (k=4 default)     |

### 3.3 Search Layer — Kiwix Encyclopedia

| Property        | Value                                      |
|-----------------|--------------------------------------------|
| Server          | Kiwix-serve                                |
| Format          | .zim compressed archives                   |
| Content         | Wikipedia, StackExchange, WikiBooks,       |
|                 | Project Gutenberg, WikiHow                 |
| Interface       | HTTP search + article retrieval            |

### 3.4 GIS Layer — Offline Maps

| Property        | Value                                      |
|-----------------|--------------------------------------------|
| Format          | MBTiles (SQLite-backed tile archives)      |
| Renderer        | MapLibre GL JS (browser-based)             |
| Data Source      | OpenStreetMap exports                      |
| Coverage        | User-defined radius (recommend 100km+)    |

### 3.5 Comms Layer — Mesh Networking

| Property        | Value                                      |
|-----------------|--------------------------------------------|
| Protocol        | Meshtastic (LoRa 915MHz/868MHz)            |
| Hardware        | Heltec V3, T-Beam, RAK WisBlock            |
| Range           | 1-10km (line of sight), mesh extends       |
| Interface       | Serial USB to VaultMind host               |

### 3.6 Knowledge Guides — Survival Domains

Pre-indexed, structured knowledge guides covering critical survival
disciplines. These are bundled as Markdown reference files that get
indexed into the RAG pipeline alongside user PDFs.

| Domain                  | Guide Module              | Key Topics                                                    |
|-------------------------|---------------------------|---------------------------------------------------------------|
| Field Medicine          | `guides/medicine/`        | Wound care, antibiotics synthesis, pain management,           |
|                         |                           | dental emergencies, childbirth, disease identification        |
| Chemistry & Pharmacy    | `guides/chemistry/`       | Aspirin synthesis, penicillin cultivation, water treatment     |
|                         |                           | chemicals, soap making, disinfectant production               |
| Energy & Fuel           | `guides/energy/`          | Wood gasification, biodiesel production, ethanol distillation,|
|                         |                           | solar panel maintenance, generator repair, battery recovery   |
| Agriculture & Foraging  | `guides/agriculture/`     | Seed saving, soil analysis, crop rotation, animal husbandry,  |
|                         |                           | wild edible identification, food preservation                 |
| Water Systems           | `guides/water/`           | Purification methods, well drilling, rainwater harvesting,    |
|                         |                           | solar distillation, testing for contaminants                  |
| Construction            | `guides/construction/`    | Shelter building, concrete mixing, basic plumbing,            |
|                         |                           | electrical wiring, fortification, sanitation systems          |
| Communications          | `guides/communications/`  | HAM radio operation, antenna building, Morse code,            |
|                         |                           | signal propagation, emergency frequencies                     |
| Metalworking & Repair   | `guides/metalworking/`    | Forge construction, basic blacksmithing, welding without      |
|                         |                           | electricity, tool making, vehicle repair                      |
| Navigation              | `guides/navigation/`      | Celestial navigation, compass use, map reading,               |
|                         |                           | dead reckoning, terrain association                           |
| Security & Defense      | `guides/security/`        | Perimeter planning, night watch protocols, conflict           |
|                         |                           | de-escalation, community organization                        |

### 3.7 System Monitor — Hardware Health

| Property        | Value                                      |
|-----------------|--------------------------------------------|
| Metrics         | CPU temp, disk health, battery level,      |
|                 | UPS status, RAID array health              |
| Alerts          | Disk degradation, thermal throttling,      |
|                 | low battery warnings                       |

---

## 4. Recommended Base Hardware

### 4.1 Primary Node — "The Vault"

The core VaultMind appliance. Optimized for low-power, high-reliability
operation on a single device.

| Component        | Recommended                    | Budget Alternative            | Notes                                     |
|------------------|--------------------------------|-------------------------------|--------------------------------------------|
| **SBC/Computer** | Intel N100 Mini PC (16GB RAM)  | Raspberry Pi 5 (8GB)         | N100 runs 8B models at ~8 tok/s            |
| **Storage**      | 2x 2TB NVMe SSD (ZFS mirror)  | 2x 1TB SATA SSD (mdadm RAID1) | Mirror = survive one drive failure        |
| **Backup**       | 1x 4TB USB HDD (cold backup)  | 1x 2TB USB HDD               | Monthly full backup of vault               |
| **Power**        | 12V 200Ah LiFePO4 battery     | 12V 100Ah AGM battery        | LiFePO4 = 3000+ cycles, 10yr lifespan     |
| **Solar**        | 200W monocrystalline panel     | 100W portable panel           | N100 draws ~15W, Pi5 draws ~8W             |
| **Charge Ctrl**  | Victron SmartSolar MPPT 75/15  | EPever Tracer 10A MPPT       | MPPT > PWM for efficiency                  |
| **Inverter**     | 300W pure sine wave            | 150W modified sine wave       | Pure sine for electronics safety           |
| **UPS**          | 12V DC UPS (mini-UPS board)    | Manual switchover             | Prevents data corruption during clouds     |
| **Networking**   | USB Ethernet + WiFi AP         | Built-in WiFi                 | Local AP for tablets/phones to query        |
| **Radio**        | Heltec V3 LoRa (Meshtastic)   | TTGO T-Beam                   | Off-grid messaging to other survivors      |
| **Enclosure**    | Pelican 1550 (waterproof)      | Ammo can + foam               | EMP/water/dust protection                  |

**Power Budget (N100 build):**
- Continuous draw: ~15-25W (VaultMind + Ollama idle/inference)
- 200Ah LiFePO4 at 12V = 2,400Wh usable capacity
- Runtime without solar: ~4-7 days continuous
- With 200W panel (5 sun-hours/day): indefinite operation

### 4.2 Mobile Node — "The Satchel"

Lightweight variant for field operations or as a secondary node.

| Component        | Recommended                    | Notes                        |
|------------------|--------------------------------|------------------------------|
| **Computer**     | Raspberry Pi 5 (8GB)           | Runs Phi-3 Mini at ~5 tok/s  |
| **Storage**      | 1TB microSD + 1TB USB SSD     | microSD for OS, SSD for data |
| **Power**        | 100Wh USB-C power bank        | ~12 hours runtime            |
| **Solar**        | 28W foldable USB-C panel      | Trickle charge in the field  |
| **Radio**        | Heltec V3 LoRa                | Mesh link back to base vault |
| **Display**      | 7" touchscreen (optional)     | Or use phone via WiFi AP     |
| **Case**         | Pelican 1200 micro             | Fits in a backpack           |

### 4.3 Storage Architecture

```
Primary Node Storage Layout:
├── /vault                    (ZFS mirror pool - 2x NVMe)
│   ├── /vault/system         OS + VaultMind application
│   ├── /vault/models         Ollama models (~10-15GB)
│   ├── /vault/index          FAISS vector index
│   ├── /vault/pdfs           PDF reference library
│   ├── /vault/zim            Kiwix .zim archives (~30-50GB)
│   ├── /vault/tiles          MBTiles map files (~2-10GB)
│   └── /vault/guides         Built-in knowledge guides
├── /backup                   (USB HDD - cold backup)
│   └── Monthly ZFS snapshots sent via zfs send/recv
└── /swap                     (Small partition on primary NVMe)
```

**Redundancy strategy:**
1. **ZFS mirror** — automatic real-time mirroring, survives 1 drive failure
2. **ZFS snapshots** — hourly snapshots, 7 days retained, rollback on corruption
3. **Cold backup** — monthly `zfs send` to USB HDD, stored separately
4. **Checksums** — ZFS verifies data integrity on every read (self-healing)

---

## 5. Knowledge Vault Content Manifest

### 5.1 Required PDF Library (~5-10GB)

These PDFs should be downloaded and indexed before deployment:

**Medical:**
- Where There Is No Doctor (Hesperian Health Guides)
- Where There Is No Dentist (Hesperian Health Guides)
- WHO Essential Medicines List
- Wilderness Medicine (Auerbach)
- Emergency War Surgery (NATO/Borden Institute)
- Tactical Combat Casualty Care Handbook

**Survival & Field Craft:**
- US Army Survival Manual (FM 21-76 / FM 3-05.70)
- SAS Survival Handbook (John Wiseman)
- US Army Ranger Handbook (SH 21-76)
- Bushcraft 101 (Dave Canterbury)

**Engineering & Construction:**
- US Army Engineer Field Manual (FM 5-34)
- The Humanure Handbook (composting sanitation)
- Pocket Ref (Thomas Glover) — engineering tables
- Machinery's Handbook (industrial reference)

**Agriculture & Food:**
- The New Self-Sufficient Gardener (John Seymour)
- Seed to Seed (Suzanne Ashworth)
- Ball Complete Book of Home Preserving
- Storey's Guide to Raising Chickens / Goats / Rabbits

**Energy & Chemistry:**
- The Knowledge: How to Rebuild Civilization (Lewis Dartnell)
- Practical Electronics for Inventors
- Chemistry: The Central Science (general reference)
- Solar Electricity Handbook

**Communications:**
- ARRL Handbook for Radio Communications
- The ARRL Antenna Book
- US Army Signal Corps Field Manual

### 5.2 Kiwix .zim Archives (~30-50GB)

| Archive                        | Size   | Content                              |
|--------------------------------|--------|--------------------------------------|
| wikipedia_en_all_nopic         | ~25GB  | Full English Wikipedia (text only)   |
| wikibooks_en_all               | ~1GB   | How-to guides and textbooks          |
| wikihow_en_all                 | ~3GB   | Step-by-step practical guides        |
| stackexchange_combined         | ~10GB  | Q&A: survival, DIY, cooking, etc.   |
| gutenberg_en_all               | ~8GB   | 60,000+ public domain books          |
| wikiversity_en_all             | ~500MB | Educational courses and lessons      |

### 5.3 Map Data (~2-10GB)

- OpenStreetMap extract for your region (100km+ radius)
- Terrain/elevation data (SRTM DEM tiles)
- Generated as MBTiles via openmaptiles or protomaps

---

## 6. Query Processing Pipeline

```
User Query
    │
    ▼
┌─────────────┐
│ Query Router │ ─── classifies query domain
└──────┬──────┘
       │
       ├──→ [1] RAG Search (FAISS)
       │         └── retrieve top-k chunks from PDF vault
       │         └── inject as context into LLM prompt
       │
       ├──→ [2] Kiwix Search
       │         └── search .zim encyclopedias
       │         └── extract article text as context
       │
       ├──→ [3] Knowledge Guides
       │         └── match query to bundled guide topics
       │         └── return structured S.T.A.R. response
       │
       └──→ [4] Direct LLM (fallback)
                 └── query model weights only
                 └── flag: "no vault context available"
                    │
                    ▼
            ┌──────────────┐
            │ S.T.A.R.     │
            │ Formatter    │
            │              │
            │ Situation    │
            │ Tools        │
            │ Action       │
            │ Risk         │
            └──────────────┘
                    │
                    ▼
              Response to User
              (with source citations)
```

---

## 7. Security Considerations

- **Air-gapped by design**: no outbound network connections post-deployment
- **Local WiFi AP**: WPA3-only, for local client devices (phones/tablets)
- **No telemetry**: zero data leaves the device, ever
- **Encrypted storage**: ZFS native encryption (aes-256-gcm) at rest
- **Physical security**: waterproof, EMP-resistant enclosure recommended

---

## 8. API Specification

### POST /api/query
Query the VaultMind knowledge base.

**Request:**
```json
{
  "query": "How do I purify water?",
  "services": ["rag", "kiwix", "guides", "llm"],
  "top_k": 4
}
```

**Response:**
```json
{
  "answer": "## Situation\n...",
  "sources": ["Where There Is No Doctor, p.42", "Wikipedia: Water purification"],
  "service": "rag",
  "confidence": "vault-backed"
}
```

### GET /api/guides
List available knowledge guide categories.

### GET /api/guides/{domain}
Get all topics in a knowledge guide domain.

### GET /api/status
System health: disk, battery, CPU temp, RAID status.

---

## 9. Deployment Checklist

- [ ] Assemble hardware (see Section 4)
- [ ] Install Ubuntu Server 24.04 LTS (or Raspberry Pi OS)
- [ ] Configure ZFS mirror pool
- [ ] Install Ollama and pull models
- [ ] Install VaultMind (`pip install -e .`)
- [ ] Run `scripts/download_data.sh` (requires internet)
- [ ] Download and place PDFs in `data/pdfs/`
- [ ] Download .zim files to `data/zim/`
- [ ] Generate MBTiles for your region to `data/tiles/`
- [ ] Run `vaultmind index` to build the FAISS index
- [ ] Start Kiwix: `kiwix-serve --port 8888 data/zim/*.zim`
- [ ] Start VaultMind: `vaultmind serve --port 8080`
- [ ] Configure local WiFi AP for client devices
- [ ] Connect Meshtastic radio (optional)
- [ ] Run cold backup to USB HDD
- [ ] Disconnect from internet — you are now air-gapped
- [ ] Test all services: `vaultmind diagnostics`
