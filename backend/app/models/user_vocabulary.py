import uuid

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
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

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "vocabulary_id",
            name="uq_user_vocabulary",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vocabulary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vocabularies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="learning",
    )

    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    review_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    user = relationship(
        "User",
        back_populates="user_vocabularies",
    )

    vocabulary = relationship(
        "Vocabulary",
        back_populates="user_vocabularies",
    )

    reviews = relationship(
        "VocabularyReview",
        back_populates="user_vocabulary",
        cascade="all, delete-orphan",
    )