import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import TradeJournal, PreopenReport, MarketOutcome
from app.schemas import TradeJournalCreate, MarketOutcomeCreate

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


def save_preopen_report(db: Session, report: dict, regime: str):
    row = PreopenReport(
        created_at=datetime.utcnow().isoformat(),
        date=report["date"],
        instrument=report["instrument"],
        regime=regime,
        primary_bias=report["primary_bias"],
        expansion_potential=report["expansion_potential"],
        report_json=json.dumps(report),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_all_preopen_reports(db: Session):
    return db.query(PreopenReport).order_by(PreopenReport.id.desc()).all()


def save_market_outcome(db: Session, outcome: MarketOutcomeCreate):
    row = MarketOutcome(**outcome.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_all_market_outcomes(db: Session):
    return db.query(MarketOutcome).order_by(MarketOutcome.id.desc()).all()


def get_preopen_report_by_date(db: Session, date: str):
    # Returns the most recent preopen report saved for that date
    return (
        db.query(PreopenReport)
        .filter(PreopenReport.date == date)
        .order_by(PreopenReport.id.desc())
        .first()
    )


def get_market_outcome_by_date(db: Session, date: str):
    return (
        db.query(MarketOutcome)
        .filter(MarketOutcome.date == date)
        .order_by(MarketOutcome.id.desc())
        .first()
    )
