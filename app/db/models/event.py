from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    league_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    season: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    week: Mapped[int | None] = mapped_column(Integer, index=True)

    # Dotted namespace: 'trade.completed', 'waiver.won', 'fa.add',
    # 'fa.drop', 'waiver.lost', 'waiver.failed', ...
    type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True,
    )

    actor_roster_id: Mapped[int | None] = mapped_column(Integer, index=True)

    # Type-specific data. Schema documented per event type in extractors.
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Provenance: where this event came from, and a stable id so we can dedupe.
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)

    # Optional back-reference to the raw row that produced it.
    raw_table: Mapped[str | None] = mapped_column(String(64))
    raw_id: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
    )
    
    subkey: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "source", "source_id", "type", "subkey",
            name="uq_event_identity",
        ),
    )