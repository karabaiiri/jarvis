import json
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.crud import (
    get_preopen_report_by_date,
    get_market_outcome_by_date,
    get_all_trades,
)

router = APIRouter()

# Normalize bias words so "bullish" == "up", "bearish" == "down", "neutral" == "mixed"
def normalize_bias(value: str) -> str:
    value = value.lower().strip()
    if value in ("bullish", "up"):
        return "bullish"
    if value in ("bearish", "down"):
        return "bearish"
    if value in ("neutral", "mixed"):
        return "neutral"
    return value

# Normalize scenario text into one of 5 fixed categories for comparison
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

@router.get("/daily-review")
def daily_review(date: str = Query(..., description="Date to review (YYYY-MM-DD)"), db: Session = Depends(get_db)):
    preopen = get_preopen_report_by_date(db, date)
    outcome = get_market_outcome_by_date(db, date)
    trades  = get_all_trades(db, trade_date=date)

    # Return a clear message if required data is missing
    if not preopen:
        return {"error": f"No preopen report found for {date}. Generate one first via /preopen-report."}
    if not outcome:
        return {"error": f"No market outcome found for {date}. Submit one first via /market-outcome."}

    report = json.loads(preopen.report_json)

    predicted_primary_bias  = report.get("primary_bias", "unknown")
    predicted_top_scenario  = report["scenarios"][0]["name"] if report.get("scenarios") else "unknown"
    actual_day_direction    = outcome.actual_day_direction
    actual_primary_move     = outcome.actual_primary_move
    best_scenario_match     = outcome.best_scenario_match

    did_bias_match         = normalize_bias(predicted_primary_bias) == normalize_bias(actual_day_direction)
    did_top_scenario_match = normalize_scenario(predicted_top_scenario) == normalize_scenario(actual_primary_move)
    trades_count           = len(trades)

    # Build overall_review string
    if did_bias_match and did_top_scenario_match:
        overall_review = "Strong read. Bias and top scenario both matched the actual market."
    elif did_bias_match:
        overall_review = "Bias was correct but the primary scenario did not play out as expected."
    elif did_top_scenario_match:
        overall_review = "Top scenario matched but bias direction was off."
    else:
        overall_review = "Neither bias nor top scenario matched. Market moved against the prediction."

    # Build improvement_note string
    if not did_bias_match and not did_top_scenario_match:
        improvement_note = "Review the scoring logic and snapshot inputs — the prediction was misaligned with price action."
    elif not did_bias_match:
        improvement_note = "Bias was wrong — check daily and H4 alignment before committing to a direction."
    elif not did_top_scenario_match:
        improvement_note = "Bias was right but scenario selection missed. Consider how the market structured itself pre-open."
    else:
        improvement_note = "Solid preparation. Keep applying the same process."

    # --- Trader alignment ---
    # Map trade_direction (long/short) to bias language (bullish/bearish)
    direction_to_bias = {"long": "bullish", "short": "bearish"}

    if not trades:
        trader_followed_predicted_bias   = None
        trader_aligned_with_actual_market = None
        trader_review = "No trades logged for this date."
    else:
        # Find the dominant trade direction (most common across all trades)
        directions = [t.trade_direction.lower() for t in trades]
        long_count  = directions.count("long")
        short_count = directions.count("short")

        if long_count > short_count:
            dominant_direction = "long"
        elif short_count > long_count:
            dominant_direction = "short"
        else:
            dominant_direction = "mixed"

        if dominant_direction == "mixed":
            trader_followed_predicted_bias    = None
            trader_aligned_with_actual_market = None
            trader_review = "Trader took both long and short trades — no clear dominant direction to evaluate."
        else:
            dominant_bias = direction_to_bias.get(dominant_direction, dominant_direction)
            trader_followed_predicted_bias    = normalize_bias(dominant_bias) == normalize_bias(predicted_primary_bias)
            trader_aligned_with_actual_market = normalize_bias(dominant_bias) == normalize_bias(actual_day_direction)

            if trader_followed_predicted_bias and trader_aligned_with_actual_market:
                trader_review = "Trader was aligned with both the prediction and the actual market direction."
            elif trader_followed_predicted_bias:
                trader_review = "Trader followed the predicted bias but the market moved in the opposite direction."
            elif trader_aligned_with_actual_market:
                trader_review = "Trader went against the prediction but happened to be aligned with where the market actually moved."
            else:
                trader_review = "Trader was misaligned with both the predicted bias and the actual market direction."

    return {
        "date": date,
        "instrument": outcome.instrument,
        "predicted_primary_bias": predicted_primary_bias,
        "predicted_top_scenario": predicted_top_scenario,
        "actual_day_direction": actual_day_direction,
        "actual_primary_move": actual_primary_move,
        "did_bias_match": did_bias_match,
        "did_top_scenario_match": did_top_scenario_match,
        "trades_count": trades_count,
        "overall_review": overall_review,
        "improvement_note": improvement_note,
        "trader_followed_predicted_bias": trader_followed_predicted_bias,
        "trader_aligned_with_actual_market": trader_aligned_with_actual_market,
        "trader_review": trader_review,
    }
