from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.crud import create_trade, get_all_trades, delete_trade
from app.schemas import TradeJournalCreate, TradeJournalResponse
from typing import List, Optional

router = APIRouter()

@router.post("/log-trade", response_model=TradeJournalResponse)
def log_trade(trade: TradeJournalCreate, db: Session = Depends(get_db)):
    return create_trade(db, trade)

@router.get("/trades", response_model=List[TradeJournalResponse])
def get_trades(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(default=None, description="Return only the newest N trades"),
    trade_date: Optional[str] = Query(default=None, description="Filter by date (YYYY-MM-DD)"),
):
    return get_all_trades(db, limit=limit, trade_date=trade_date)

@router.delete("/trades/{trade_id}")
def remove_trade(trade_id: int, db: Session = Depends(get_db)):
    trade = delete_trade(db, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return {"message": f"Trade {trade_id} deleted successfully"}
