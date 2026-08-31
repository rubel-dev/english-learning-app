from datetime import datetime
import uuid
from sqlalchemy import CheckConstraint, DateTime, Integer, String, Text, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from sqlalchemy.dialects.postgresql import JSONB, UUID

class GlobalAiExplanation(Base):
    __tablename__ = 'global_ai_explanations'
    id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True, 
        default=uuid.uuid4
    )
    reading_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("readings.id", ondelete='CASCADE'),
        nullable=False
    )
    start_position: Mapped[int] = mapped_column(
        Integer,
        nullable=False
        
    )
    end_position: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    selected_text:Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    result : Mapped[object] = mapped_column(
        JSONB,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default=func.now(),
        nullable=False
    )
 
    __table_args__ = (
        UniqueConstraint(
            "reading_id",
            "start_position",
            "end_position",
            "type",
            name="uq_reading_selected_text_type",
        ),
        CheckConstraint(
            "type IN ('vocabulary', 'sentence', 'passage')",
            name="check_type",
        ),
    )
     
