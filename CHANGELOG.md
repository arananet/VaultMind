# Changelog

All notable changes to VaultMind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-22

### Added
- **SPEC.md** — Full system specification document covering architecture,
  hardware recommendations, storage strategy, and deployment checklist.
- **CHANGELOG.md** — This file; spec-driven development tracking.
- **Knowledge Guides** — 10 survival domain guides bundled as structured
  Markdown, indexed into the RAG pipeline:
  - Medicine: wound care, antibiotics cultivation, pain relief synthesis,
    dental emergencies, childbirth, disease identification.
  - Chemistry & Pharmacy: aspirin synthesis, penicillin cultivation,
    activated charcoal, soap making, disinfectant production.
  - Energy & Fuel: wood gasification, biodiesel from vegetable oil,
    ethanol distillation, solar maintenance, generator repair, battery recovery.
  - Agriculture: seed saving, crop rotation, soil building, animal husbandry,
    wild edible identification, food preservation (canning, smoking, drying).
  - Water Systems: purification methods (boiling, solar, chemical, filter),
    well drilling, rainwater harvesting, contaminant testing.
  - Construction: shelter types, concrete/mortar mixing, basic plumbing,
    electrical wiring, sanitation systems, fortification.
  - Communications: HAM radio basics, antenna building, Morse code,
    emergency frequencies, signal propagation.
  - Metalworking: forge construction, blacksmithing basics, tool making,
    brazing/soldering, vehicle repair.
  - Navigation: celestial navigation, compass/map reading, dead reckoning,
    terrain association, GPS-free wayfinding.
  - Security: perimeter planning, watch protocols, community organization,
    conflict de-escalation, resource management.
- **Hardware Recommendations** — Detailed base hardware specs in SPEC.md
  and README.md covering:
  - Primary Node ("The Vault"): Intel N100 + ZFS mirror + LiFePO4 solar
  - Mobile Node ("The Satchel"): Raspberry Pi 5 + power bank + foldable solar
  - Redundant storage architecture with ZFS snapshots and cold backup
- **System Monitor** (`vaultmind/services/monitor.py`) — CPU temperature,
  disk health, battery status, RAID array monitoring.
- **Diagnostics CLI** (`vaultmind diagnostics`) — Pre-flight check for all
  VaultMind services and hardware health.
- **Guide search API** — `/api/guides` and `/api/guides/{domain}` endpoints.
- **Expanded S.T.A.R. system prompt** — Now covers 15+ survival domains
  with explicit anti-hallucination rules per domain.
- **Guide indexer** — `vaultmind index --include-guides` indexes bundled
  knowledge guides into the FAISS vector store alongside user PDFs.

### Changed
- **README.md** — Complete rewrite with hardware BOM, knowledge catalog,
  deployment guide, and quick-reference survival topic index.
- **System prompt** — Expanded from 5 to 15+ expert domains.
- **Query router** — Now includes knowledge guide search as priority layer.
- **Config** — Added guide, monitor, and hardware sections to vaultmind.yaml.
- **Download script** — Expanded with comprehensive PDF/ZIM recommendations.

## [0.1.0] - 2026-03-22

### Added
- Initial project scaffolding and architecture.
- RAG engine: PDF ingestion via PyMuPDF, FAISS vector store,
  sentence-transformers embeddings, Ollama LLM integration.
- Protocol Zero system prompt with S.T.A.R. response method.
- Kiwix .zim file search integration for offline Wikipedia/StackExchange.
- MBTiles tile server with MapLibre GL JS viewer for offline GIS.
- Meshtastic LoRa bridge for off-grid mesh messaging.
- Unified query router with fallback chain: RAG → Kiwix → Direct LLM.
- Rich CLI with `index`, `query`, `chat`, and `serve` commands.
- Flask web UI with terminal-aesthetic interface.
- Docker Compose stack (VaultMind + Ollama + Kiwix).
- Test suite for prompt, ingestion, Kiwix, and tile modules.
- Data download helper script.
