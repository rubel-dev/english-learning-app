 

from enum import Enum
import uuid

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ListeningType(str, Enum):
    PRACTICE = "practice"
    ENJOY = "enjoy"


class ListeningLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"


class Listening(Base):
    __tablename__ = "listenings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4


    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    embedded_link: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    type: Mapped[ListeningType] = mapped_column(
        SQLEnum(ListeningType, name="listening_type"),
        nullable=False,
    )

    level: Mapped[ListeningLevel | None] = mapped_column(
        SQLEnum(ListeningLevel, name="listening_level"),
        nullable=True,
    )

    questions: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    segments: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )