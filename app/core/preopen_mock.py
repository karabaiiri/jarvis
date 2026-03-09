from app.core.market_mock import get_mock_market_snapshot
from app.core.scoring import get_primary_bias, get_expansion_potential
from app.core.scenarios import get_scenarios

def get_mock_preopen_report():
    snapshot = get_mock_market_snapshot()
    primary_bias = get_primary_bias(snapshot)
    expansion_potential = get_expansion_potential(snapshot)
    scenarios = get_scenarios(primary_bias, snapshot)

    return {
        "date": snapshot["date"],
        "instrument": snapshot["instrument"],
        "report_time": "2026-03-07T08:30:00-05:00",
        "primary_bias": primary_bias,
        "snapshot": snapshot,
        "scenarios": scenarios,
        "expansion_potential": expansion_potential,
        "notes_to_trader": "Wait for NY open confirmation before entering. Avoid chasing moves above PDH without pullback.",
    }
