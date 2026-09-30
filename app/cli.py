import argparse
import asyncio

from app.db.database import SessionLocal
from app.sync.sleeper import SleeperSyncService


def parse_weeks(spec: str) -> list[int]:
    """'1-18' -> [1..18]; '1,3,5' -> [1,3,5]"""
    if "-" in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in spec.split(",")]


async def _backfill_matchups(league_id: str, weeks: list[int]) -> None:
    with SessionLocal() as db:
        svc = SleeperSyncService(db)
        league = await svc.sync_league(league_id)

        total = 0
        for week in weeks:
            count = await svc.sync_matchups(
                league_id,
                league.id,
                league.season,
                week,
            )
            total += count
            print(f"week {week:>2}: {count} roster-rows")

        print(f"done: {total} rows across {len(weeks)} weeks")


def main() -> None:
    parser = argparse.ArgumentParser(prog="app")
    sub = parser.add_subparsers(dest="cmd", required=True)

    mb = sub.add_parser(
        "backfill-matchups",
        help="Pull matchups for a league from Sleeper into Postgres",
    )
    mb.add_argument("--league", required=True, help="Sleeper league id")
    mb.add_argument("--weeks", default="1-18", help="'1-18' or '1,3,5'")

    args = parser.parse_args()

    if args.cmd == "backfill-matchups":
        asyncio.run(_backfill_matchups(args.league, parse_weeks(args.weeks)))


if __name__ == "__main__":
    main()