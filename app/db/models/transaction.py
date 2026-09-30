from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    league_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    sleeper_transaction_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    type: Mapped[str | None] = mapped_column(
        String(50),
        index=True,
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
    )

    creator: Mapped[str | None] = mapped_column(
        String(32),
        index=True,
    )

    # Sleeper returns epoch milliseconds (e.g. 1789533944005) — needs 64-bit
    created_at_sleeper: Mapped[int | None] = mapped_column(
        BigInteger,
    )

    roster_ids: Mapped[list | None] = mapped_column(
        JSONB,
    )

    adds: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    drops: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    waiver_bid: Mapped[int | None] = mapped_column(
        Integer,
    )

    draft_picks: Mapped[list | None] = mapped_column(
        JSONB,
    )

    transaction_json: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    
    notes: Mapped[str | None] = mapped_column(
        String(255)
    )