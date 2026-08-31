
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




class WritingState(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
     

class UserWritingState(Base):
    __tablename__ = "user_writing_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    writing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("writings.id", ondelete="CASCADE"),
        nullable=False,
    )

    state: Mapped[WritingState] = mapped_column(
        Enum(WritingState, name="writing_state"),
        nullable=False,
        default=WritingState.ACTIVE,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "writing_id",
            name="uq_user_writing_state",
        ),
    )

    writing = relationship(
        "Writing",
        back_populates="user_states",
    )