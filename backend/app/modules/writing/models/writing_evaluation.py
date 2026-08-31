import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WritingEvaluation(Base):
    __tablename__ = "writing_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    writing_submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "writing_submissions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    corrections: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    alternative: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    takeaways: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    submission = relationship(
        "WritingSubmission",
        back_populates="evaluation",
    )
