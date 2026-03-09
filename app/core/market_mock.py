def get_mock_market_snapshot():
    return {
        "date": "2026-03-07",
        "instrument": "NQ",
        "daily_bias": "bullish",
        "h4_bias": "bullish",
        "h1_bias": "neutral",
        "pdh": 18450.25,
        "pdl": 18210.50,
        "onh": 18380.00,
        "onl": 18290.75,
        "pmh": 18500.00,
        "pml": 18100.00,
        "vwap": 18342.50,
        "directional_score": 7,
        "expansion_score": 6,
        "day_quality": "A",
        # price position
        "above_or_below_vwap": "above",
        "inside_or_outside_prior_day_range": "inside",
        # news
        "has_830_news": True,
        "news_bias": "bullish",
        "news_volatility_risk": "medium",
        # premarket structure
        "premarket_structure": "higher_highs",
        "holds_vwap": True,
        "compression_before_open": False,
        "sweep_detected_preopen": False,
    }
