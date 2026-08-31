# app/models/listening_answer.py

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from app.db.base import Base
from sqlalchemy.dialects.postgresql import JSONB, UUID

class ListeningAnswer(Base):
    __tablename__ = "listening_answers"

    id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4 
        )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    listening_id: Mapped[int] = mapped_column(
        ForeignKey("listenings.id", ondelete="CASCADE"),
        nullable=False,
    )

    question_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    selected_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "listening_id",
            "question_id",
            name="uq_user_listening_question_answer",
        ),
    )