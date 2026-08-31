import uuid

from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

class Assessment(Base):
    __tablename__ = 'assessments'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True, 
        default=uuid.uuid4
    )
    content: Mapped[object] = mapped_column(
        JSONB,
        nullable=False
    )
    assessment_results = relationship("AssessmentResult", back_populates='assessment')