import argparse
import asyncio
import json

from app.db.database import SessionLocal
from app.sync.sleeper import SleeperSyncService


def parse_weeks(spec: str) -> list[int]:
    if "-" in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in spec.split(",")]


# ---------------------------------------------------------------- matchups
async def _backfill_matchups(league_id: str, weeks: list[int]) -> None:
    with SessionLocal() as db:
        svc = SleeperSyncService(db)
        league = await svc.sync_league(league_id)
        total = 0
        for week in weeks:
            count = await svc.sync_matchups(league_id, league.id, league.season, week)
            total += count
            print(f"week {week:>2}: {count} roster-rows")
        print(f"done: {total} rows across {len(weeks)} weeks")


# ---------------------------------------------------------------- events
async def _rebuild_events(league_sleeper_id: str) -> None:
    from sqlalchemy import select
    from app.db.models import League
    from app.events.rebuild import rebuild_events_for_league

    with SessionLocal() as db:
        league = db.scalar(select(League).where(League.sleeper_id == league_sleeper_id))
        if league is None:
            print(f"no league with sleeper_id={league_sleeper_id} — run sync first")
            return
        n = rebuild_events_for_league(db, league.id)
        print(f"rebuilt {n} events for league {league.id}")


# ---------------------------------------------------------------- trade review
async def _review_trade(event_id: int) -> None:
    from app.commissioner.cases import open_trade_review

    with SessionLocal() as db:
        case, decision = open_trade_review(db, event_id)

    print(f"case #{case.id} → {decision.decision} "
          f"(confidence {decision.confidence:.2f}, risk {decision.risk_level})")
    print()
    print(decision.reasoning)
    print()
    print("evidence:")
    for e in (decision.evidence or []):
        print(f"  - {e}")


async def _show_case(case_id: int) -> None:
    from sqlalchemy import select
    from app.db.models import CommissionerCase, CommissionerDecision

    with SessionLocal() as db:
        case = db.get(CommissionerCase, case_id)
        if case is None:
            print(f"no case with id={case_id}")
            return
        decisions = db.scalars(
            select(CommissionerDecision).where(CommissionerDecision.case_id == case_id)
        ).all()
        print(json.dumps({
            "case": {
                "id": case.id, "type": case.type, "status": case.status,
                "title": case.title, "opened_at": str(case.opened_at),
                "subject_event_ids": case.subject_event_ids,
            },
            "decisions": [
                {
                    "id": d.id, "decision": d.decision,
                    "confidence": d.confidence, "risk": d.risk_level,
                    "reasoning": d.reasoning, "evidence": d.evidence,
                    "model": d.model_name, "decided_at": str(d.decided_at),
                }
                for d in decisions
            ],
        }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="app")
    sub = parser.add_subparsers(dest="cmd", required=True)

    mb = sub.add_parser("backfill-matchups")
    mb.add_argument("--league", required=True)
    mb.add_argument("--weeks", default="1-18")

    rb = sub.add_parser("rebuild-events")
    rb.add_argument("--league", required=True)

    rt = sub.add_parser("review-trade")
    rt.add_argument("--event", type=int, required=True,
                    help="event id of a trade.completed event")

    sc = sub.add_parser("show-case")
    sc.add_argument("--case", type=int, required=True)

    args = parser.parse_args()

    if args.cmd == "backfill-matchups":
        asyncio.run(_backfill_matchups(args.league, parse_weeks(args.weeks)))
    elif args.cmd == "rebuild-events":
        asyncio.run(_rebuild_events(args.league))
    elif args.cmd == "review-trade":
        asyncio.run(_review_trade(args.event))
    elif args.cmd == "show-case":
        asyncio.run(_show_case(args.case))


if __name__ == "__main__":
    main()