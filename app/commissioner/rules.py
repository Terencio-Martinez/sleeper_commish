from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Event
from app.sleeper.players import player_name


@dataclass
class TradeSide:
    roster_id: int
    gives_players: list[str]
    receives_players: list[str]
    gives_picks: list[dict]
    receives_picks: list[dict]


@dataclass
class TradeEvidence:
    trade_id: str
    occurred_at: datetime
    parties: list[TradeSide]
    prior_trades_between_parties: int
    last_trade_between_parties: datetime | None
    prior_decisions_on_these_rosters: list[dict] = field(default_factory=list)


def _names(ids) -> list[str]:
    return [player_name(pid) for pid in (ids or [])]


def _split_picks(picks, mine, partner):
    gives, receives = [], []
    for pk in picks or []:
        if pk.get("roster_id") == mine:
            gives.append(pk)
        elif pk.get("roster_id") == partner:
            receives.append(pk)
    return gives, receives


def gather_trade_evidence(db: Session, event: Event) -> TradeEvidence:
    sides = db.scalars(
        select(Event).where(
            Event.source == "sleeper",
            Event.source_id == event.source_id,
            Event.type == "trade.completed",
        )
    ).all()

    payload = event.payload or {}
    adds = payload.get("adds") or {}      # {player_id: roster_receiving}
    drops = payload.get("drops") or {}    # {player_id: roster_giving}
    picks = payload.get("draft_picks") or []

    roster_ids = sorted({s.actor_roster_id for s in sides if s.actor_roster_id is not None})

    parties: list[TradeSide] = []
    for rid in roster_ids:
        partner = next((x for x in roster_ids if x != rid), -1)
        received = [pid for pid, r in adds.items() if r == rid]
        gave = [pid for pid, r in drops.items() if r == rid]
        gp, rp = _split_picks(picks, rid, partner)
        parties.append(TradeSide(
            roster_id=rid,
            gives_players=_names(gave),
            receives_players=_names(received),
            gives_picks=gp,
            receives_picks=rp,
        ))

    # Prior trades between same pair
    prior_events = db.scalars(
        select(Event).where(
            Event.league_id == event.league_id,
            Event.type == "trade.completed",
            Event.occurred_at < event.occurred_at,
            Event.source_id != event.source_id,
        )
    ).all()

    by_source: dict[str, list[Event]] = defaultdict(list)
    for e in prior_events:
        by_source[e.source_id].append(e)

    target = set(roster_ids)
    prior_count = 0
    last: datetime | None = None
    for _, evs in by_source.items():
        pair = {e.actor_roster_id for e in evs if e.actor_roster_id is not None}
        if pair == target:
            prior_count += 1
            local_max = max(e.occurred_at for e in evs)
            if last is None or local_max > last:
                last = local_max

    return TradeEvidence(
        trade_id=event.source_id,
        occurred_at=event.occurred_at,
        parties=parties,
        prior_trades_between_parties=prior_count,
        last_trade_between_parties=last,
        prior_decisions_on_these_rosters=[],  # TODO: wire to commissioner_decisions
    )