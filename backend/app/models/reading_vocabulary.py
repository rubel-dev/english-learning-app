import uuid

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReadingVocabulary(Base):
    __tablename__ = "reading_vocabularies"

    __table_args__ = (
        UniqueConstraint(
            "reading_id",
            "vocabulary_id",
            name="uq_reading_vocabulary",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    reading_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("readings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vocabulary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vocabularies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reading = relationship(
        "Reading",
        back_populates="vocabulary_links",
    )

    vocabulary = relationship(
        "Vocabulary",
        back_populates="reading_links",
    )