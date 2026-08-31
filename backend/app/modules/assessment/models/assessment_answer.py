
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint

from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class AssessmentAnswer(Base):
    __tablename__ = 'assessment_answers'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid= True),
        ForeignKey("users.id"),
        nullable=False

    )
    question_id:Mapped[Integer] = mapped_column(
        Integer
    )
    selected_answer:Mapped[str] = mapped_column(
        String(2),
        nullable=False
    )
    __table_args__ = (
            UniqueConstraint(
                "user_id",
                "question_id",
                name="uq_user_question",
            ),
            CheckConstraint(
                "selected_answer IN ('a', 'b', 'c', 'd')",
                name = 'check_assessment_answer_option'
            )
        )
