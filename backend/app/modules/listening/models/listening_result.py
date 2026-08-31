

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid
from app.db.base import Base


class ListeningResult(Base):
    __tablename__ = "listening_results"

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

    score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "listening_id",
            name="uq_user_listening_result",
        ),
    )