import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReadingResult(Base):
    __tablename__ = "reading_results"

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

    reading_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("readings.id", ondelete="CASCADE"),
        nullable=False,
    )

    highest_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    first_completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "reading_id",
            name="uq_user_reading_result",
        ),
        CheckConstraint(
            "highest_score >= 0 AND highest_score <= 5",
            name = "check_reading_highest_score"
        ),
        CheckConstraint(
            "status IN ('spaced_repetition', 'fully_completed')",
            name="check_reading_result_status"
        )
    )

    reading = relationship(
        "Reading",
        back_populates="results",
    )

    user = relationship(
        "User",
        back_populates="reading_results",
    )