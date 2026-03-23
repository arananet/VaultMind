# Changelog

All notable changes to VaultMind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-23

### Added
- **Database layer** — PostgreSQL (primary) with SQLite edge fallback,
  SQLAlchemy 2.0 ORM, Alembic migrations. 8 tables: Document, Chunk,
  QueryLog, GuideEntry, SensorLog, MeshMessage, AutomationRule, TTSCache.
  Schema docs endpoint (`GET /api/schema`) and stats (`GET /api/db/stats`).
- **Offline TTS** — Multi-backend text-to-speech engine supporting Piper TTS
  (CPU/edge, 15-65MB), Chatterbox TTS (GPU, 4.5GB VRAM), Kokoro TTS
  (CPU, 82M params), and espeak-ng (fallback). Exposed via `POST /api/tts`.
- **Hardware control** — gpiod-based GPIO control, I2C sensor reading,
  ADC for solar/battery voltage monitoring, USB relay control, and a
  rule-based automation engine for sensor-triggered actions.
- **Flask app factory** — Proper `create_app()` pattern with Blueprints,
  replaces inline route handlers. Serves React static build or Open WebUI.
- **REST API blueprint** — `POST /api/query`, `GET /api/guides`,
  `GET /api/guides/<domain>`, `GET /api/status`, `POST /api/tts`,
  `GET /api/schema`, `GET /api/db/stats`. Query logging to database.
- **React frontend** — React 19 + Vite with dark terminal aesthetic,
  glassmorphism accents, WCAG AA contrast ratios. Pages: QueryPage
  (with domain chips and TTS button), GuidesPage (card grid with markdown),
  DiagnosticsPage (status table).
- **International radio guide** — New `radio_international` domain covering
  ITU regions, international HF band plan, distress frequencies, emergency
  nets (IARN, SATERN), NATO phonetic alphabet, Q-codes, regional frequency
  guides, HF station setup, and digital modes (JS8Call, VARA, FT8).
- **Physical placement guide** — Site selection criteria, recommended
  locations (Tier 1-4), environmental controls, EMP/Faraday protection,
  concealment strategies, mobile node placement, maintenance schedules.
- **ITX+GPU hardware tiers** — 4-tier hardware recommendation system:
  Tier 1 "Satchel" (Pi 5, 8W), Tier 2 "Vault" (N100, 15-25W),
  Tier 3 "Forge" (ITX+RTX 4060 Ti, 65-220W), Tier 4 "Citadel" (workstation).
  Includes GPU selection guide, reasoning model minimum requirements table,
  and power budgets with solar sizing.
- **Open WebUI support** — `--open-webui` flag on `vaultmind serve` to proxy
  to Open WebUI as alternative frontend.

### Changed
- **LLM models** — Replaced all unverified model references with verified
  Ollama tags: `qwen3:8b` (primary, 5.2GB), `qwen3:4b` (lightweight, 2.5GB),
  `qwen3:0.6b` (tiny, 523MB), `phi4-reasoning` (reasoning, 11GB),
  `phi4-mini-reasoning` (edge reasoning, 3.2GB). All tags verified against
  the Ollama library as of March 2026.
- **Config** — `vaultmind.yaml` now includes database, TTS, hardware control,
  and automation sections. Model names updated across all config files.
- **Docker Compose** — Added PostgreSQL 16 service, optional Open WebUI
  service (commented), NVIDIA GPU reservation for Ollama.
- **pyproject.toml** — Version bumped to 0.3.0. Added dependencies:
  sqlalchemy, alembic, psycopg2-binary, requests. New optional groups:
  tts, tts-gpu, hardware, dev (with ruff).
- **Download script** — Updated `ollama pull` commands to verified tags.
- **SPEC.md** — Version 0.3.0 with expanded architecture, new service
  layers (DB, TTS, Hardware), ITX+GPU hardware tiers, reasoning model
  specs, power budgets, and API endpoints for TTS/schema.
- **Guide domains** — Expanded from 10 to 11 with `radio_international`.

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
