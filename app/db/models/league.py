from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    sleeper_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    sport: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    season: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    season_type: Mapped[str | None] = mapped_column(
        String(50),
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
    )

    total_rosters: Mapped[int | None] = mapped_column(
        Integer,
    )

    scoring_settings: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    settings: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    raw_data: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )