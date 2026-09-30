from app.db.database import Base, engine

# Import all models so SQLAlchemy registers them
from app.db.models import (
    League,
    LeagueUser,
    Roster,
    Player,
    Matchup,
    Transaction,
)

Base.metadata.create_all(bind=engine)

print("Database tables initialized.")