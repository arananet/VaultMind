"""Knowledge guide indexer and search for bundled survival guides."""

from __future__ import annotations

import logging
from pathlib import Path

from langchain.schema import Document

logger = logging.getLogger(__name__)

DEFAULT_GUIDES_DIR = "data/guides"

GUIDE_DOMAINS = {
    "medicine": "Field Medicine, Wound Care, Antibiotics, Pain Management, Dental, Childbirth",
    "chemistry": "Soap Making, Disinfectants, Activated Charcoal, Water Chemicals, Preservation",
    "energy": "Wood Gasification, Biodiesel, Ethanol Distillation, Solar, Generator, Battery",
    "agriculture": "Seed Saving, Crop Rotation, Composting, Animal Husbandry, Foraging, Preservation",
    "water": "Purification, Bio-Sand Filter, Solar Distillation, Wells, Rainwater, Testing",
    "construction": "Shelter, Concrete, Lime Mortar, Plumbing, Electrical, Sanitation",
    "communications": "HAM Radio, Antennas, Morse Code, Meshtastic, Frequencies, Propagation",
    "metalworking": "Forge Building, Blacksmithing, Tool Making, Brazing, Vehicle Repair",
    "navigation": "Compass, Celestial Navigation, Dead Reckoning, Pace Counting, Terrain",
    "security": "Community Organization, Perimeter Defense, Watch Protocols, OPSEC, Barter",
}


def load_guides(guides_dir: str = DEFAULT_GUIDES_DIR) -> list[Document]:
    """Load all bundled knowledge guides as LangChain Documents."""
    guides_path = Path(guides_dir)
    if not guides_path.is_dir():
        logger.warning("Guides directory not found: %s", guides_path)
        return []

    documents = []
    for md_file in sorted(guides_path.rglob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
            domain = md_file.parent.name
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source_file": md_file.name,
                        "domain": domain,
                        "source_type": "guide",
                        "topics": GUIDE_DOMAINS.get(domain, "General"),
                    },
                )
            )
            logger.info("Loaded guide: %s/%s", domain, md_file.name)
        except Exception:
            logger.exception("Failed to load guide: %s", md_file)

    logger.info("Loaded %d knowledge guides", len(documents))
    return documents


def list_domains(guides_dir: str = DEFAULT_GUIDES_DIR) -> dict[str, dict]:
    """List all available guide domains and their topics."""
    guides_path = Path(guides_dir)
    result = {}
    for domain, topics in GUIDE_DOMAINS.items():
        domain_path = guides_path / domain
        files = sorted(domain_path.glob("*.md")) if domain_path.is_dir() else []
        result[domain] = {
            "topics": topics,
            "files": [f.name for f in files],
            "available": len(files) > 0,
        }
    return result


def get_guide_content(domain: str, guides_dir: str = DEFAULT_GUIDES_DIR) -> str | None:
    """Get the full content of a specific guide domain."""
    domain_path = Path(guides_dir) / domain
    if not domain_path.is_dir():
        return None

    parts = []
    for md_file in sorted(domain_path.glob("*.md")):
        parts.append(md_file.read_text(encoding="utf-8"))

    return "\n\n---\n\n".join(parts) if parts else None
