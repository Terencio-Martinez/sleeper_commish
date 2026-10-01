from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class CommissionerCase(Base):
    __tablename__ = "commissioner_cases"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    league_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    season: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    week: Mapped[int | None] = mapped_column(Integer, index=True)

    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True, default="open",
    )

    submitted_by_sleeper_user_id: Mapped[str | None] = mapped_column(String(32))
    subject_event_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    opened_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)


class CommissionerDecision(Base):
    __tablename__ = "commissioner_decisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    case_id: Mapped[int] = mapped_column(
        ForeignKey("commissioner_cases.id"), nullable=False, index=True,
    )

    decision: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    confidence: Mapped[float | None] = mapped_column(Float)
    risk_level: Mapped[str | None] = mapped_column(String(16))

    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list | None] = mapped_column(JSONB)
    recommended_action: Mapped[dict | None] = mapped_column(JSONB)

    human_approval_required: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )
    human_approved_by: Mapped[str | None] = mapped_column(String(32))
    decided_by: Mapped[str] = mapped_column(String(16), nullable=False)

    precedent_decision_ids: Mapped[list | None] = mapped_column(JSONB)

    model_name: Mapped[str | None] = mapped_column(String(64))
    raw_response: Mapped[dict | None] = mapped_column(JSONB)

    decided_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True,
    )