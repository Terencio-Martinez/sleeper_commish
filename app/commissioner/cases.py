from datetime import datetime

from sqlalchemy.orm import Session

from app.ai.client import judge_trade
from app.commissioner.rules import gather_trade_evidence
from app.db.models import CommissionerCase, CommissionerDecision, Event


def open_trade_review(db: Session, event_id: int):
    event = db.get(Event, event_id)
    if event is None:
        raise ValueError(f"no event with id={event_id}")
    if event.type != "trade.completed":
        raise ValueError(f"event {event_id} is {event.type}, expected trade.completed")

    evidence = gather_trade_evidence(db, event)

    case = CommissionerCase(
        league_id=event.league_id,
        season=event.season,
        week=event.week,
        type="trade_review",
        status="open",
        subject_event_ids=[event.id],
        title=f"Trade review: {evidence.trade_id}",
    )
    db.add(case)
    db.flush()

    result = judge_trade(evidence)

    decision = CommissionerDecision(
        case_id=case.id,
        decision=result.decision,
        confidence=result.confidence,
        risk_level=result.risk_level,
        reasoning=result.reasoning,
        evidence=result.evidence,
        recommended_action=result.recommended_action,
        human_approval_required=result.human_approval_required,
        decided_by="ai",
        model_name=result.model_name,
        raw_response=result.raw_response,
    )
    db.add(decision)

    case.status = "decided"
    case.closed_at = datetime.utcnow()

    db.commit()
    db.refresh(case)
    db.refresh(decision)
    return case, decision