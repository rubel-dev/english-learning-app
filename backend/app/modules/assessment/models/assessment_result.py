
from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func

from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
class AssessmentResult(Base):
    __tablename__ = 'assessment_results'
    id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete = 'CASCADE'),
        unique=True,
        nullable=False,
        
    )
    assessment_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id"),
        nullable=False,
        index = True

    )
    score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,

    )
    level: Mapped[str] = mapped_column(
        String(2),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )
    __table_args__ = (
        CheckConstraint(
            "level IN ('A1', 'A2', 'B1', 'B2')",
            name="check_assessment_level",
        ),
        CheckConstraint(
            "status IN ('completed', 'skipped')",
            name="check_assessment_status",
        ),
        CheckConstraint(
            """
            (status = 'completed' AND score IS NOT NULL)
            OR
            (status = 'skipped' AND score IS NULL)
            """,
            name="check_assessment_result_score",
        ),
        CheckConstraint(
            """
            (status = 'skipped' AND level = 'A1')
            OR
            (status = 'completed' AND level IN ('A1', 'A2', 'B1', 'B2'))
            """,
            name="check_assessment_result_level",
        ),
)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default=func.now(),
        nullable=False
    )
    user = relationship("User", back_populates='assessment_result')
    assessment = relationship("Assessment", back_populates='assessment_results')

    