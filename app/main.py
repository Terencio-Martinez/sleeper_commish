from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.db.models import League
from app.sleeper.client import SleeperClient
from app.sync.sleeper import SleeperSyncService
from app.sync.transactions import TransactionSyncService


app = FastAPI(
    title="AI Fantasy Football Commissioner",
    version="0.1.0",
)

sleeper = SleeperClient()


@app.get("/")
def root():
    return {
        "name": "AI Fantasy Football Commissioner",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/sleeper/league")
async def sleeper_league():
    try:
        return await sleeper.get_league(
            settings.sleeper_league_id
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Sleeper API request failed: {exc}",
        )


@app.post("/sync")
async def sync(
    db: Session = Depends(get_db),
):
    service = SleeperSyncService(db)

    league = await service.sync_league(
        settings.sleeper_league_id
    )

    return {
        "status": "success",
        "league_id": league.sleeper_id,
        "league_name": league.name,
        "season": league.season,
        "teams": league.total_rosters,
    }

@app.post("/sync/transactions/{week}")
async def sync_transactions(
    week: int,
    db: Session = Depends(get_db),
):
    service = TransactionSyncService(db)

    return await service.sync_week(
        settings.sleeper_league_id,
        week,
    )