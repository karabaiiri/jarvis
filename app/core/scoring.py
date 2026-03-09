def get_primary_bias(snapshot: dict) -> str:
    """
    Scores 7 signals. Each bullish signal = +1, bearish = -1, neutral = 0.
    Final score >= 3  → bullish
    Final score <= -3 → bearish
    Anything in between → neutral
    """
    score = 0

    # Timeframe biases
    for key in ["daily_bias", "h4_bias", "h1_bias"]:
        if snapshot[key] == "bullish":
            score += 1
        elif snapshot[key] == "bearish":
            score -= 1

    # Price position relative to VWAP
    if snapshot["above_or_below_vwap"] == "above":
        score += 1
    elif snapshot["above_or_below_vwap"] == "below":
        score -= 1

    # News alignment
    if snapshot["news_bias"] == "bullish":
        score += 1
    elif snapshot["news_bias"] == "bearish":
        score -= 1

    # VWAP hold in premarket
    if snapshot["holds_vwap"] is True:
        score += 1
    elif snapshot["holds_vwap"] is False:
        score -= 1

    # Premarket structure
    if snapshot["premarket_structure"] == "higher_highs":
        score += 1
    elif snapshot["premarket_structure"] == "lower_lows":
        score -= 1

    if score >= 3:
        return "bullish"
    if score <= -3:
        return "bearish"
    return "neutral"


def get_expansion_potential(snapshot: dict) -> str:
    """
    Starts from expansion_score (0-10), then adds points for:
    - News volatility risk (high = +2, medium = +1, only if has_830_news)
    - Compression before open = +1 (tight range = energy building)
    - Sweep detected preopen = +1 (stop hunt = potential momentum)

    Final score >= 9 → high
    Final score >= 6 → medium
    Below 6        → low
    """
    score = snapshot["expansion_score"]

    if snapshot["has_830_news"]:
        if snapshot["news_volatility_risk"] == "high":
            score += 2
        elif snapshot["news_volatility_risk"] == "medium":
            score += 1

    if snapshot["compression_before_open"]:
        score += 1

    if snapshot["sweep_detected_preopen"]:
        score += 1

    if score >= 9:
        return "high"
    if score >= 6:
        return "medium"
    return "low"
