from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Roster(Base):
    __tablename__ = "rosters"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    sleeper_roster_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    league_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    owner_sleeper_user_id: Mapped[str | None] = mapped_column(
        String(32),
        index=True,
    )

    roster_json: Mapped[dict | None] = mapped_column(
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