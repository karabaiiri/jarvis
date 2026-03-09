import json
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.core.preopen_mock import get_mock_preopen_report
from app.db.database import get_db
from app.db.crud import save_preopen_report, get_all_preopen_reports

router = APIRouter()

@router.get("/preopen-report")
def preopen_report(regime: str = Query(default="bullish"), date: str = Query(default=None), db: Session = Depends(get_db)):
    report = get_mock_preopen_report(regime, date)
    save_preopen_report(db, report, regime)
    return report

@router.get("/preopen-reports")
def list_preopen_reports(db: Session = Depends(get_db)):
    rows = get_all_preopen_reports(db)
    return [json.loads(row.report_json) for row in rows]
