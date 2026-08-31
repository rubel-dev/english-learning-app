from datetime import datetime
import uuid

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
class VocabularyReview(Base):
    __tablename__ = "vocabulary_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_vocabulary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_vocabularies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    stage_before: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    stage_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "action IN ('MASTER', 'NOT_MASTER')",
            name="check_vocabulary_review_action",
        ),
        CheckConstraint(
            "stage_before >= 1 AND stage_before <= 8",
            name="check_review_stage_before",
        ),
        CheckConstraint(
            "stage_after >= 1 AND stage_after <= 8",
            name="check_review_stage_after",
        ),
        Index(
            "ix_vocabulary_reviews_user_vocabulary_id",
            "user_vocabulary_id",
        ),
        Index(
            "ix_vocabulary_reviews_reviewed_at",
            "reviewed_at",
        ),
    )

    user_vocabulary = relationship(
        "UserVocabulary",
        back_populates="reviews",
    )