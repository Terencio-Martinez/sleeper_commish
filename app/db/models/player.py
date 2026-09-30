from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    sleeper_player_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    last_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    position: Mapped[str | None] = mapped_column(
        String(20),
    )

    team: Mapped[str | None] = mapped_column(
        String(10),
    )

    raw_data: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )