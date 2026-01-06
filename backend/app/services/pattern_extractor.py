"""Pattern extraction service using 3-pass evidence-anchored pipeline."""

import json
import logging
from dataclasses import dataclass

from app.config import ModelID
from app.services.llm_client import LLMClient, LLMError
from app.services.prompts.evidence_inventory import (
    EVIDENCE_INVENTORY_SYSTEM,
    EVIDENCE_INVENTORY_USER,
    EvidenceInventory,
    parse_evidence_inventory,
)
from app.services.prompts.extraction import (
    EXTRACTION_SYSTEM,
    EXTRACTION_USER,
    ExtractionResult,
    parse_extraction_result,
)
from app.services.prompts.verification import (
    VERIFICATION_SYSTEM,
    VERIFICATION_USER,
    VerificationResult,
    VerificationStatus,
    compute_verification_status,
    parse_verification_result,
)

logger = logging.getLogger(__name__)

# Maximum characters for paper text input
MAX_TEXT_CHARS = 50_000

# Temperature settings for each pass
EVIDENCE_TEMP = 0.2  # Low for consistent extraction
EXTRACTION_TEMP = 0.2  # Low for reproducibility
VERIFICATION_TEMP = 0.1  # Very low for consistency


@dataclass
class PatternExtractionResult:
    """Complete result from 3-pass extraction pipeline."""

    patterns: ExtractionResult
    evidence_inventory: EvidenceInventory
    verification: VerificationResult
    warnings: list[str]

    @property
    def is_successful(self) -> bool:
        """Return True if extraction completed without critical errors."""
        return self.verification.verification_status != VerificationStatus.fail

    @property
    def pattern_count(self) -> int:
        """Return number of extracted patterns."""
        return len(self.patterns.patterns)


class PatternExtractor:
    """Extracts patterns from papers using 3-pass evidence-anchored pipeline.

    Pass 1 (Haiku): Extract evidence inventory from paper
    Pass 2 (Sonnet): Extract patterns with [E#] citations
    Pass 3 (Haiku): Verify extraction quality
    """

    def __init__(
        self,
        haiku_client: LLMClient | None = None,
        sonnet_client: LLMClient | None = None,
    ) -> None:
        """Initialize pattern extractor.

        Args:
            haiku_client: LLM client for Pass 1 and 3. Creates default if not provided.
            sonnet_client: LLM client for Pass 2. Creates default if not provided.
        """
        self._haiku_client = haiku_client
        self._sonnet_client = sonnet_client

    def _ensure_haiku(self) -> LLMClient:
        """Lazily initialize Haiku client."""
        if self._haiku_client is None:
            self._haiku_client = LLMClient(model=ModelID.HAIKU_3_5)
        return self._haiku_client

    def _ensure_sonnet(self) -> LLMClient:
        """Lazily initialize Sonnet client."""
        if self._sonnet_client is None:
            self._sonnet_client = LLMClient(model=ModelID.SONNET_4)
        return self._sonnet_client

    async def extract(
        self,
        text: str,
        metadata_context: str | None = None,
    ) -> PatternExtractionResult:
        """Extract patterns from paper text using 3-pass pipeline.

        Args:
            text: Paper content text.
            metadata_context: Optional metadata to include in extraction context.

        Returns:
            PatternExtractionResult with patterns, evidence, and verification.
        """
        warnings: list[str] = []

        # Truncate long text
        truncated_text = text[:MAX_TEXT_CHARS] if text else ""
        if len(text) > MAX_TEXT_CHARS:
            warnings.append(
                f"Text truncated from {len(text)} to {MAX_TEXT_CHARS} characters"
            )

        # Pass 1: Evidence Inventory (Haiku)
        try:
            evidence_inventory = await self._extract_evidence(truncated_text)
            item_count = len(evidence_inventory.evidence_items)
            logger.info(f"Pass 1 complete: {item_count} evidence items")
        except LLMError as e:
            logger.error(f"Pass 1 failed: {e}")
            return self._failed_result(str(e))

        # Pass 2: Pattern Extraction (Sonnet)
        try:
            extraction_result = await self._extract_patterns(
                truncated_text, evidence_inventory, metadata_context
            )
            logger.info(f"Pass 2 complete: {len(extraction_result.patterns)} patterns")
        except LLMError as e:
            logger.error(f"Pass 2 failed: {e}")
            return self._failed_result(str(e), evidence_inventory)

        # Pass 3: Verification (Haiku)
        try:
            verification_result = await self._verify_extraction(
                evidence_inventory, extraction_result
            )
            logger.info(
                f"Pass 3 complete: status={verification_result.verification_status}"
            )
        except LLMError as e:
            logger.warning(f"Pass 3 failed: {e}")
            # Verification failure is non-fatal - return patterns with warning
            warnings.append(f"Verification failed: {e}")
            verification_result = VerificationResult(
                verification_status=VerificationStatus.warn,
                improvement_suggestions=[
                    "Verification pass failed - manual review recommended"
                ],
            )

        # Build warnings from verification
        warnings.extend(self._build_warnings(verification_result))

        return PatternExtractionResult(
            patterns=extraction_result,
            evidence_inventory=evidence_inventory,
            verification=verification_result,
            warnings=warnings,
        )

    async def _extract_evidence(self, text: str) -> EvidenceInventory:
        """Pass 1: Extract evidence inventory from paper."""
        client = self._ensure_haiku()

        user_prompt = EVIDENCE_INVENTORY_USER.format(text=text)

        response = await client.complete_json(
            system_prompt=EVIDENCE_INVENTORY_SYSTEM,
            user_prompt=user_prompt,
            temperature=EVIDENCE_TEMP,
        )

        return parse_evidence_inventory(response)

    async def _extract_patterns(
        self,
        text: str,
        evidence: EvidenceInventory,
        metadata_context: str | None = None,
    ) -> ExtractionResult:
        """Pass 2: Extract patterns with evidence citations."""
        client = self._ensure_sonnet()

        # Format evidence inventory for prompt
        evidence_str = self._format_evidence_inventory(evidence)

        # Add metadata context if provided
        full_text = text
        if metadata_context:
            full_text = f"[Metadata: {metadata_context}]\n\n{text}"

        user_prompt = EXTRACTION_USER.format(
            evidence_inventory=evidence_str,
            text=full_text,
        )

        response = await client.complete_json(
            system_prompt=EXTRACTION_SYSTEM,
            user_prompt=user_prompt,
            temperature=EXTRACTION_TEMP,
        )

        return parse_extraction_result(response)

    async def _verify_extraction(
        self,
        evidence: EvidenceInventory,
        extraction: ExtractionResult,
    ) -> VerificationResult:
        """Pass 3: Verify extraction quality."""
        client = self._ensure_haiku()

        # Format inputs for verification prompt
        evidence_str = self._format_evidence_inventory(evidence)
        patterns_str = self._format_patterns(extraction)

        user_prompt = VERIFICATION_USER.format(
            evidence_inventory=evidence_str,
            patterns=patterns_str,
        )

        response = await client.complete_json(
            system_prompt=VERIFICATION_SYSTEM,
            user_prompt=user_prompt,
            temperature=VERIFICATION_TEMP,
        )

        result = parse_verification_result(response)

        # Validate/override LLM status with computed status
        computed_status = compute_verification_status(result)
        if computed_status != result.verification_status:
            logger.info(
                f"Overriding LLM status {result.verification_status} "
                f"with computed status {computed_status}"
            )
            result.verification_status = computed_status

        return result

    def _format_evidence_inventory(self, evidence: EvidenceInventory) -> str:
        """Format evidence inventory for inclusion in prompts."""
        lines = [f"Paper: {evidence.paper_title}", ""]
        for item in evidence.evidence_items:
            lines.append(f"[{item.id}] ({item.type}, {item.importance})")
            lines.append(f"  Location: {item.location}")
            lines.append(f'  Quote: "{item.quote}"')
            lines.append("")
        return "\n".join(lines)

    def _format_patterns(self, extraction: ExtractionResult) -> str:
        """Format extracted patterns for verification prompt."""
        patterns_data = []
        for p in extraction.patterns:
            patterns_data.append(
                {
                    "rank": p.rank,
                    "name": p.name,
                    "claim": p.claim,
                    "evidence": p.evidence,
                    "context": p.context,
                    "evidence_ids": p.evidence_ids,
                }
            )
        return json.dumps(patterns_data, indent=2)

    def _build_warnings(self, verification: VerificationResult) -> list[str]:
        """Build warning messages from verification result."""
        warnings = []

        # Add citation issues as warnings
        for issue in verification.citation_issues:
            warnings.append(
                f"Pattern {issue.pattern_rank} ({issue.field}): {issue.issue}"
            )

        # Add accuracy concerns as warnings
        for concern in verification.accuracy_concerns:
            msg = f"Pattern {concern.pattern_rank} [{concern.evidence_id}]: "
            msg += concern.concern
            warnings.append(msg)

        # Add unused evidence warning if significant
        if len(verification.unused_evidence) > 3:
            warnings.append(
                f"Unused evidence: {', '.join(verification.unused_evidence[:5])}"
                + ("..." if len(verification.unused_evidence) > 5 else "")
            )

        return warnings

    def _failed_result(
        self,
        error_message: str,
        evidence: EvidenceInventory | None = None,
    ) -> PatternExtractionResult:
        """Create a failed extraction result."""
        return PatternExtractionResult(
            patterns=ExtractionResult(patterns=[], gaps_identified=[error_message]),
            evidence_inventory=evidence or EvidenceInventory(paper_title="Unknown"),
            verification=VerificationResult(
                verification_status=VerificationStatus.fail,
                improvement_suggestions=[f"Extraction failed: {error_message}"],
            ),
            warnings=[f"Extraction failed: {error_message}"],
        )
