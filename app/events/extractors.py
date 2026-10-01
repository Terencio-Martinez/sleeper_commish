from datetime import datetime, timezone

from app.db.models import Transaction


def _ms_to_dt(ms: int | None) -> datetime | None:
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).replace(tzinfo=None)


def extract_transaction_events(txn: Transaction) -> list[dict]:
    events: list[dict] = []

    occurred = _ms_to_dt(txn.created_at_sleeper) or txn.created_at
    source_id = txn.sleeper_transaction_id

    base = {
        "league_id": txn.league_id,
        "season": None,
        "week": None,
        "occurred_at": occurred,
        "source": "sleeper",
        "source_id": source_id,
        "raw_table": "transactions",
        "raw_id": txn.id,
    }

    ttype = txn.type
    status = txn.status

    if ttype == "trade" and status == "complete":
        for roster_id in (txn.roster_ids or []):
            events.append({
                **base,
                "type": "trade.completed",
                "subkey": f"roster:{roster_id}",
                "actor_roster_id": roster_id,
                "payload": {
                    "roster_ids": txn.roster_ids,
                    "adds": txn.adds,
                    "drops": txn.drops,
                    "draft_picks": txn.draft_picks,
                },
            })
        return events

    if ttype == "waiver":
        if status == "complete":
            for player_id, roster_id in (txn.adds or {}).items():
                events.append({
                    **base,
                    "type": "waiver.won",
                    "subkey": f"player:{player_id}",
                    "actor_roster_id": roster_id,
                    "payload": {
                        "player_id": player_id,
                        "bid": txn.waiver_bid,
                        "drops": txn.drops,
                    },
                })
        elif status == "failed":
            for player_id, roster_id in (txn.adds or {}).items():
                events.append({
                    **base,
                    "type": "waiver.lost",
                    "subkey": f"player:{player_id}",
                    "actor_roster_id": roster_id,
                    "payload": {
                        "player_id": player_id,
                        "bid": txn.waiver_bid,
                    },
                })
        return events

    if ttype == "free_agent":
        if status == "complete":
            for player_id, roster_id in (txn.adds or {}).items():
                events.append({
                    **base,
                    "type": "fa.add",
                    "subkey": f"player:{player_id}",
                    "actor_roster_id": roster_id,
                    "payload": {"player_id": player_id},
                })
            for player_id, roster_id in (txn.drops or {}).items():
                events.append({
                    **base,
                    "type": "fa.drop",
                    "subkey": f"player:{player_id}",
                    "actor_roster_id": roster_id,
                    "payload": {"player_id": player_id},
                })
        return events

    return events