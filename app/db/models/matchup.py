from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Matchup(Base):
    __tablename__ = "matchups"

    id: Mapped[int] = mapped_column(primary_key=True)

    league_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    season: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    # Sleeper groups two rosters into a matchup by this id.
    # NULL for bye weeks / teams with no opponent.
    matchup_id: Mapped[int | None] = mapped_column(
        Integer,
        index=True,
    )

    roster_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    points: Mapped[float | None] = mapped_column(Float)

    starters: Mapped[list | None] = mapped_column(JSONB)
    starters_points: Mapped[list | None] = mapped_column(JSONB)
    players: Mapped[list | None] = mapped_column(JSONB)
    players_points: Mapped[dict | None] = mapped_column(JSONB)
    custom_points: Mapped[float | None] = mapped_column(Float)

    matchup_json: Mapped[dict | None] = mapped_column(JSONB)

    synced_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "league_id",
            "season",
            "week",
            "roster_id",
            name="uq_matchup_league_season_week_roster",
        ),
    )