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


class UserVocabulary(Base):
    __tablename__ = "user_vocabularies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    learning_content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "vocabulary_learning_contents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    stage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "learning_content_id",
            name="uq_user_learning_content",
        ),
        CheckConstraint(
            "status IN ('active', 'mastered')",
            name="check_user_vocabulary_status",
        ),
        CheckConstraint(
            "stage >= 1 AND stage <= 8",
            name="check_user_vocabulary_stage",
        ),
        Index(
            "ix_user_vocabularies_due",
            "user_id",
            "status",
            "next_review_at",
        ),
    )

    user = relationship(
        "User",
        back_populates="user_vocabularies",
    )

    learning_content = relationship(
        "VocabularyLearningContent",
        back_populates="user_vocabularies",
    )

    reviews = relationship(
        "VocabularyReview",
        back_populates="user_vocabulary",
        cascade="all, delete-orphan",
    )
