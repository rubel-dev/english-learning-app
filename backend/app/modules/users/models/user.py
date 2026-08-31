import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class User(Base):
    __tablename__='users'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True, 
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default='user'
    )
    current_level: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default='A1'
    )
   
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    __table_args__ = (
            CheckConstraint(
                "current_level IN ('A1', 'A2', 'B1', 'B2')",
                name="check_current_level",
            ),
        )

    assessment_result = relationship("AssessmentResult", back_populates='user')
    user_reading_completions = relationship('UserReadingCompletion', back_populates='user')
    user_vocabularies = relationship('UserVocabulary', back_populates='user')
    reading_sessions = relationship(
    "ReadingSession",
    back_populates="user",
    cascade="all, delete-orphan",
    )

    reading_results = relationship(
        "ReadingResult",
        back_populates="user",
        cascade="all, delete-orphan",
    )