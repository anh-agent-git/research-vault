"""Pattern model for extracted insights."""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.paper import Paper


def _utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(UTC)


class PatternStatus(str, Enum):
    """Review status of a pattern."""

    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Pattern(Base):
    """Structured insight extracted from a paper using Claim/Evidence/Context."""

    __tablename__ = "patterns"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    paper_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )

    # Pattern identification
    name: Mapped[str] = mapped_column(String(200))  # 3-6 word pattern name

    # Content fields (at least one must be non-null for valid pattern)
    claim: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    custom_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Vector store reference
    embedding_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[PatternStatus] = mapped_column(
        SQLEnum(PatternStatus), default=PatternStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now, onupdate=_utc_now
    )

    # Relationship to paper
    paper: Mapped["Paper"] = relationship(back_populates="patterns")

    __table_args__ = (
        Index("idx_patterns_paper_id", "paper_id"),
        Index("idx_patterns_status", "status"),
        Index("idx_patterns_paper_status", "paper_id", "status"),
    )

    @property
    def has_valid_content(self) -> bool:
        """Return True if at least one content field is set and non-empty."""
        return bool(self.claim or self.evidence or self.context)

    @property
    def content_fields(self) -> list[str]:
        """Return list of non-null content field names in order."""
        fields = []
        if self.claim:
            fields.append("claim")
        if self.evidence:
            fields.append("evidence")
        if self.context:
            fields.append("context")
        return fields
