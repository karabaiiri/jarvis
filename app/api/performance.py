import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.crud import get_all_preopen_reports, get_all_market_outcomes, get_all_trades

router = APIRouter()

# Same helpers as in review.py — used to compare bias and scenario types
def normalize_bias(value: str) -> str:
    value = value.lower().strip()
    if value in ("bullish", "up"):
        return "bullish"
    if value in ("bearish", "down"):
        return "bearish"
    if value in ("neutral", "mixed"):
        return "neutral"
    return value

def normalize_scenario(text: str) -> str:
    text = text.lower()
    if "sweep" in text or "reversal" in text:
        return "sweep_reversal"
    if "range" in text or "consolidation" in text:
        return "range"
    if "bullish" in text:
        return "bullish_continuation"
    if "bearish" in text:
        return "bearish_continuation"
    return "unknown"

def safe_rate(numerator: int, denominator: int):
    # Returns a 0.0-1.0 ratio, or None if there is no data
    if denominator == 0:
        return None
    return round(numerator / denominator, 2)

@router.get("/performance-summary")
def performance_summary(db: Session = Depends(get_db)):
    preopen_rows = get_all_preopen_reports(db)
    outcome_rows = get_all_market_outcomes(db)
    all_trades   = get_all_trades(db)

    # Index by date — first one wins since rows are ordered newest first
    preopen_by_date = {}
    for row in preopen_rows:
        if row.date not in preopen_by_date:
            preopen_by_date[row.date] = row

    outcome_by_date = {}
    for row in outcome_rows:
        if row.date not in outcome_by_date:
            outcome_by_date[row.date] = row

    # Group trades by date
    trades_by_date = {}
    for trade in all_trades:
        trades_by_date.setdefault(trade.date, []).append(trade)

    # Only count dates that have both a preopen report and a market outcome
    reviewed_dates = set(preopen_by_date.keys()) & set(outcome_by_date.keys())
    total_reviewed_days = len(reviewed_dates)

    bias_matches         = 0
    scenario_matches     = 0
    trader_aligned_days  = 0
    days_with_trades     = 0

    for date in reviewed_dates:
        preopen = preopen_by_date[date]
        outcome = outcome_by_date[date]

        report             = json.loads(preopen.report_json)
        predicted_bias     = report.get("primary_bias", "unknown")
        predicted_scenario = report["scenarios"][0]["name"] if report.get("scenarios") else "unknown"

        # Did the bias match?
        if normalize_bias(predicted_bias) == normalize_bias(outcome.actual_day_direction):
            bias_matches += 1

        # Did the top scenario match?
        if normalize_scenario(predicted_scenario) == normalize_scenario(outcome.actual_primary_move):
            scenario_matches += 1

        # Did the trader align with the actual market direction?
        trades = trades_by_date.get(date, [])
        if trades:
            days_with_trades += 1
            directions  = [t.trade_direction.lower() for t in trades]
            long_count  = directions.count("long")
            short_count = directions.count("short")

            if long_count > short_count:
                dominant_bias = "bullish"
            elif short_count > long_count:
                dominant_bias = "bearish"
            else:
                dominant_bias = None  # mixed — skip

            if dominant_bias and normalize_bias(dominant_bias) == normalize_bias(outcome.actual_day_direction):
                trader_aligned_days += 1

    # Trade stats
    total_trades   = len(all_trades)
    winning_trades = sum(1 for t in all_trades if t.points_result > 0)
    losing_trades  = sum(1 for t in all_trades if t.points_result < 0)
    avg_points     = round(sum(t.points_result for t in all_trades) / total_trades, 2) if total_trades > 0 else None

    return {
        "total_reviewed_days":     total_reviewed_days,
        "bias_match_rate":         safe_rate(bias_matches, total_reviewed_days),
        "top_scenario_match_rate": safe_rate(scenario_matches, total_reviewed_days),
        "trader_alignment_rate":   safe_rate(trader_aligned_days, days_with_trades),
        "total_trades":            total_trades,
        "average_points_result":   avg_points,
        "winning_trades":          winning_trades,
        "losing_trades":           losing_trades,
    }
