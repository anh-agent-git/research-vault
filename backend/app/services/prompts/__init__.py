"""LLM prompt templates for extraction and synthesis."""

from app.services.prompts.evidence_inventory import (
    EVIDENCE_INVENTORY_SYSTEM,
    EVIDENCE_INVENTORY_USER,
    EvidenceImportance,
    EvidenceInventory,
    EvidenceItem,
    EvidenceType,
    parse_evidence_inventory,
)
from app.services.prompts.metadata import (
    METADATA_EXTRACTION_SYSTEM,
    METADATA_EXTRACTION_USER,
)

__all__ = [
    # Evidence Inventory (Pass 1)
    "EVIDENCE_INVENTORY_SYSTEM",
    "EVIDENCE_INVENTORY_USER",
    "EvidenceImportance",
    "EvidenceInventory",
    "EvidenceItem",
    "EvidenceType",
    "parse_evidence_inventory",
    # Metadata Extraction
    "METADATA_EXTRACTION_SYSTEM",
    "METADATA_EXTRACTION_USER",
]
