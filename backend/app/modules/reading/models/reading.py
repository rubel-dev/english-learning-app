import uuid

from sqlalchemy import CheckConstraint, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base
class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    passage: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    reading_level: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    estimated_reading_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    quiz: Mapped[object] = mapped_column(
        JSONB,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "reading_level IN ('A1', 'A2', 'B1', 'B2')",
            name="check_reading_level",
        ),
        CheckConstraint(
            "estimated_reading_time > 0",
            name="check_estimated_reading_time",
        ),
    )
    user_reading_completions = relationship('UserReadingCompletion', back_populates='reading')
    
    sessions = relationship(
        "ReadingSession",
        back_populates="reading",
        cascade="all, delete-orphan",
    )

    results = relationship(
        "ReadingResult",
        back_populates="reading",
        cascade="all, delete-orphan",
    )