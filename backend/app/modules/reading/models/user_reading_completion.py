from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID

class UserReadingCompletion(Base):
    __tablename__ ='user_reading_completions'
    user_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
    reading_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('readings.id'),
        primary_key=True,
        nullable=False
    )
   
    completed_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    user = relationship('User', back_populates='user_reading_completions')
    reading = relationship('Reading', back_populates='user_reading_completions')