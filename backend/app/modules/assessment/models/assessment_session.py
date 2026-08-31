
from datetime import datetime
import uuid

from sqlalchemy import   DateTime, ForeignKey, func

from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

class AssessmentSession(Base):
    __tablename__ = 'assessment_sessions'
    user_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey('users.id'),
        primary_key=True,
        nullable=False
       
    )
    
    assessment_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id"),
        primary_key=True,
        nullable=False, 

    ) 
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default=func.now(),
        nullable=False
    )


    