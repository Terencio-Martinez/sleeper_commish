from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import League, Transaction
from app.sleeper.client import SleeperClient


class TransactionSyncService:

    def __init__(self, db: Session):
        self.db = db
        self.sleeper = SleeperClient()

    async def sync_week(
        self,
        league_id: str,
        week: int,
    ):

        league = self.db.scalar(
            select(League).where(
                League.sleeper_id == league_id
            )
        )

        if league is None:
            raise ValueError(
                f"League {league_id} has not been synced."
            )

        transactions = (
            await self.sleeper.get_transactions(
                league_id,
                week,
            )
        )

        created = 0
        updated = 0

        for data in transactions:

            transaction_id = data["transaction_id"]

            transaction = self.db.scalar(
                select(Transaction).where(
                    Transaction.sleeper_transaction_id
                    == transaction_id
                )
            )

            if transaction is None:
                transaction = Transaction(
                    sleeper_transaction_id=transaction_id,
                    league_id=league.id,
                )

                self.db.add(transaction)
                created += 1

            else:
                updated += 1

            transaction.type = data.get("type")
            transaction.status = data.get("status")
            transaction.creator = data.get("creator")

            transaction.created_at_sleeper = data.get(
                "created"
            )

            transaction.roster_ids = data.get(
                "roster_ids"
            )

            transaction.adds = data.get(
                "adds"
            )

            transaction.drops = data.get(
                "drops"
            )

            transaction.waiver_bid = data.get(
                "waiver_bid"
            )

            transaction.draft_picks = data.get(
                "draft_picks"
            )

            transaction.transaction_json = data

        self.db.commit()

        return {
            "week": week,
            "total": len(transactions),
            "created": created,
            "updated": updated,
        }