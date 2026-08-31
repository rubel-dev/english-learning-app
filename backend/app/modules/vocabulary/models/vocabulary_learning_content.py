# vocabulary_learning_content.py

from datetime import datetime
import uuid

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VocabularyLearningContent(Base):
    __tablename__ = "vocabulary_learning_contents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    vocabulary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "vocabularies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    bangla_meaning: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    example_context: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Polymorphic source reference.
    # Validated in service/application layer.
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "source_type IN "
            "('reading', 'speaking', 'ielts', 'writing', 'manual')",
            name="check_vocabulary_content_source_type",
        ),
        Index(
            "ix_vocabulary_learning_contents_vocabulary_id",
            "vocabulary_id",
        ),
        Index(
            "ix_vocabulary_learning_contents_source",
            "source_type",
            "source_id",
        ),
    )

    vocabulary = relationship(
        "Vocabulary",
        back_populates="learning_contents",
    )

    user_vocabularies = relationship(
        "UserVocabulary",
        back_populates="learning_content",
        cascade="all, delete-orphan",
    )