from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import Event, League, Transaction
from app.events.extractors import extract_transaction_events


def rebuild_events_for_league(
    db: Session,
    internal_league_id: int,
) -> int:
    """Wipe and re-derive all events for one league from raw tables.

    Idempotent by construction: deletes then rebuilds. The unique
    constraint on (source, source_id, type) protects against double
    inserts if we change this later.
    """
    league = db.get(League, internal_league_id)
    if league is None:
        raise ValueError(f"league {internal_league_id} not found")

    db.execute(
        delete(Event).where(
            Event.league_id == internal_league_id,
            Event.source == "sleeper",
        )
    )
    db.flush()

    txns = db.scalars(
        select(Transaction).where(
            Transaction.league_id == internal_league_id,
        )
    ).all()

    inserted = 0
    for txn in txns:
        for ev in extract_transaction_events(txn):
            ev["season"] = league.season
            # Best-effort: leave week=None for now — you can backfill from
            # matchup timing later if you need it.
            db.add(Event(**ev))
            inserted += 1

    db.commit()
    return inserted