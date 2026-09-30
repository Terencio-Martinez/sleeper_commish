from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Matchup(Base):
    __tablename__ = "matchups"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    league_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    season: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    matchup_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    roster_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    points: Mapped[float | None] = mapped_column()

    starters: Mapped[list | None] = mapped_column(
        JSONB,
    )

    players: Mapped[list | None] = mapped_column(
        JSONB,
    )

    matchup_json: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )