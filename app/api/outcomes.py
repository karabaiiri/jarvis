from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.crud import save_market_outcome, get_all_market_outcomes
from app.schemas import MarketOutcomeCreate, MarketOutcomeResponse

router = APIRouter()

@router.post("/market-outcome", response_model=MarketOutcomeResponse)
def create_market_outcome(outcome: MarketOutcomeCreate, db: Session = Depends(get_db)):
    return save_market_outcome(db, outcome)

@router.get("/market-outcomes", response_model=list[MarketOutcomeResponse])
def list_market_outcomes(db: Session = Depends(get_db)):
    return get_all_market_outcomes(db)
