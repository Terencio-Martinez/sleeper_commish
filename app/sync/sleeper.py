from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import League, LeagueUser, Roster
from app.sleeper.client import SleeperClient


class SleeperSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.sleeper = SleeperClient()

    async def sync_league(self, league_id: str) -> League:
        league_data = await self.sleeper.get_league(
            league_id
        )

        league = self.db.scalar(
            select(League).where(
                League.sleeper_id == league_id
            )
        )

        if league is None:
            league = League(
                sleeper_id=league_id,
            )
            self.db.add(league)

        league.name = league_data["name"]
        league.sport = league_data["sport"]
        league.season = league_data["season"]
        league.season_type = league_data.get("season_type")
        league.status = league_data.get("status")
        league.total_rosters = league_data.get("total_rosters")
        league.scoring_settings = league_data.get(
            "scoring_settings"
        )
        league.settings = league_data.get("settings")
        league.metadata_json = league_data.get(
            "metadata"
        )
        league.raw_data = league_data

        self.db.commit()
        self.db.refresh(league)

        await self.sync_users(league_id)
        await self.sync_rosters(
            league_id,
            league.id,
        )

        return league

    async def sync_users(self, league_id: str):
        users = await self.sleeper.get_users(
            league_id
        )

        for user_data in users:
            sleeper_user_id = user_data["user_id"]

            user = self.db.scalar(
                select(LeagueUser).where(
                    LeagueUser.sleeper_user_id
                    == sleeper_user_id
                )
            )

            if user is None:
                user = LeagueUser(
                    sleeper_user_id=sleeper_user_id
                )
                self.db.add(user)

            user.display_name = user_data.get(
                "display_name"
            )

            user.avatar = user_data.get(
                "avatar"
            )

            user.is_bot = user_data.get(
                "is_bot",
                False,
            )

        self.db.commit()

    async def sync_rosters(
        self,
        league_id: str,
        internal_league_id: int,
    ):
        rosters = await self.sleeper.get_rosters(
            league_id
        )

        for roster_data in rosters:
            roster_id = roster_data["roster_id"]

            roster = self.db.scalar(
                select(Roster).where(
                    Roster.league_id
                    == internal_league_id,
                    Roster.sleeper_roster_id
                    == roster_id,
                )
            )

            if roster is None:
                roster = Roster(
                    sleeper_roster_id=roster_id,
                    league_id=internal_league_id,
                )
                self.db.add(roster)

            roster.owner_sleeper_user_id = (
                roster_data.get("owner_id")
            )

            roster.roster_json = roster_data

        self.db.commit()