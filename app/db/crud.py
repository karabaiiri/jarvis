from sqlalchemy.orm import Session
from app.db.models import TradeJournal
from app.schemas import TradeJournalCreate

def create_trade(db: Session, trade: TradeJournalCreate):
    db_trade = TradeJournal(**trade.model_dump())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

def delete_trade(db: Session, trade_id: int):
    trade = db.query(TradeJournal).filter(TradeJournal.id == trade_id).first()
    if not trade:
        return None
    db.delete(trade)
    db.commit()
    return trade


def get_all_trades(db: Session, limit: int = None, trade_date: str = None):
    query = db.query(TradeJournal)
    if trade_date:
        query = query.filter(TradeJournal.date == trade_date)
    query = query.order_by(TradeJournal.id.desc())
    if limit:
        query = query.limit(limit)
    return query.all()
