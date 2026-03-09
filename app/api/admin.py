# Development cleanup endpoints — use these to reset data during testing
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import TradeJournal, PreopenReport, MarketOutcome

router = APIRouter(prefix="/admin")

@router.delete("/clear-trades")
def clear_trades(db: Session = Depends(get_db)):
    count = db.query(TradeJournal).delete()
    db.commit()
    return {"message": f"Deleted {count} trade(s) from the database."}

@router.delete("/clear-preopen-reports")
def clear_preopen_reports(db: Session = Depends(get_db)):
    count = db.query(PreopenReport).delete()
    db.commit()
    return {"message": f"Deleted {count} preopen report(s) from the database."}

@router.delete("/clear-market-outcomes")
def clear_market_outcomes(db: Session = Depends(get_db)):
    count = db.query(MarketOutcome).delete()
    db.commit()
    return {"message": f"Deleted {count} market outcome(s) from the database."}
