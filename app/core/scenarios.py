def get_scenarios(primary_bias: str, snapshot: dict) -> list:
    """
    Returns exactly 3 scenarios. Logic depends on:
    - primary_bias: sets the primary scenario direction
    - sweep_detected_preopen: replaces scenario 2 with a sweep/reversal play
    - news_bias, above_or_below_vwap, holds_vwap, premarket_structure:
      used in trigger and invalidation text to make them more specific
    Probabilities are integers that add up to 100.
    """
    onh  = snapshot["onh"]
    onl  = snapshot["onl"]
    pdh  = snapshot["pdh"]
    pdl  = snapshot["pdl"]
    vwap = snapshot["vwap"]

    sweep       = snapshot["sweep_detected_preopen"]
    news_bias   = snapshot["news_bias"]
    above_vwap  = snapshot["above_or_below_vwap"] == "above"
    holds_vwap  = snapshot["holds_vwap"]
    structure   = snapshot["premarket_structure"]

    # --- helper: build context-aware trigger detail ---
    def vwap_context():
        if holds_vwap and above_vwap:
            return f"price is holding above VWAP at {vwap}"
        if not holds_vwap and not above_vwap:
            return f"price is failing below VWAP at {vwap}"
        return f"VWAP at {vwap} is the key pivot"

    def structure_detail():
        if structure == "higher_highs":
            return "premarket is printing higher highs"
        if structure == "lower_lows":
            return "premarket is printing lower lows"
        return "premarket is ranging"

    def news_detail():
        if news_bias == "bullish":
            return "news bias is bullish — favors continuation higher"
        if news_bias == "bearish":
            return "news bias is bearish — risk of sharp reversal"
        return "news bias is neutral"

    # --- sweep/reversal scenario (replaces scenario 2 when sweep occurred) ---
    sweep_reversal_bullish = {
        "name": "Post-sweep bullish reversal",
        "probability": 25,
        "trigger": f"Sweep below ONL at {onl} already occurred — look for reclaim and reversal above {onl}",
        "invalidation": f"Price continues lower below {pdl}",
        "target": f"ONH at {onh} after reclaim of VWAP at {vwap}",
    }

    sweep_reversal_bearish = {
        "name": "Post-sweep bearish reversal",
        "probability": 25,
        "trigger": f"Sweep above ONH at {onh} already occurred — look for rejection and reversal below {onh}",
        "invalidation": f"Price continues higher above {pdh}",
        "target": f"ONL at {onl} after break below VWAP at {vwap}",
    }

    # --- BULLISH primary ---
    if primary_bias == "bullish":
        scenario_1 = {
            "name": "Bullish continuation above ONH",
            "probability": 60,
            "trigger": (
                f"Price reclaims ONH at {onh}. "
                f"{structure_detail().capitalize()}, {vwap_context()}, {news_detail()}."
            ),
            "invalidation": f"Price fails back below VWAP at {vwap} on a closing basis",
            "target": f"PDH at {pdh}",
        }
        scenario_2 = sweep_reversal_bearish if sweep else {
            "name": "Rejection at ONH — fade back to discount",
            "probability": 25,
            "trigger": f"Price spikes into ONH at {onh} and shows a reversal candle or exhaustion",
            "invalidation": f"Sustained break and close above {onh}",
            "target": f"ONL at {onl}",
        }
        scenario_3 = {
            "name": "Range between ONL and ONH",
            "probability": 15,
            "trigger": f"Price stays between {onl} and {onh} — no clear direction through London open",
            "invalidation": f"Clean breakout above {onh} or below {onl}",
            "target": f"VWAP at {vwap}",
        }
        return [scenario_1, scenario_2, scenario_3]

    # --- BEARISH primary ---
    if primary_bias == "bearish":
        scenario_1 = {
            "name": "Bearish continuation below ONL",
            "probability": 60,
            "trigger": (
                f"Price breaks and holds below ONL at {onl}. "
                f"{structure_detail().capitalize()}, {vwap_context()}, {news_detail()}."
            ),
            "invalidation": f"Price reclaims VWAP at {vwap} and holds above it",
            "target": f"PDL at {pdl}",
        }
        scenario_2 = sweep_reversal_bullish if sweep else {
            "name": "Bullish reclaim of VWAP",
            "probability": 25,
            "trigger": f"Price drives up through VWAP at {vwap} with momentum and holds",
            "invalidation": f"Price fails back below ONL at {onl}",
            "target": f"ONH at {onh}",
        }
        scenario_3 = {
            "name": "Range between ONL and VWAP",
            "probability": 15,
            "trigger": f"Price oscillates between {onl} and {vwap} — no expansion",
            "invalidation": f"Clean break below {onl} or above {vwap}",
            "target": f"Midpoint at {round((onl + vwap) / 2, 2)}",
        }
        return [scenario_1, scenario_2, scenario_3]

    # --- NEUTRAL primary ---
    if sweep:
        return [
            {
                "name": "Post-sweep reversal play",
                "probability": 45,
                "trigger": f"Preopen sweep detected — look for reversal after reclaim of ONH at {onh} or ONL at {onl}",
                "invalidation": f"Price extends beyond {pdh} or {pdl} without reversal",
                "target": f"VWAP at {vwap}",
            },
            {
                "name": "Bullish breakout above ONH",
                "probability": 30,
                "trigger": f"Price breaks above ONH at {onh} with momentum. {news_detail()}.",
                "invalidation": f"Price falls back below VWAP at {vwap}",
                "target": f"PDH at {pdh}",
            },
            {
                "name": "Bearish breakdown below ONL",
                "probability": 25,
                "trigger": f"Price breaks below ONL at {onl} and holds. {vwap_context()}.",
                "invalidation": f"Price reclaims VWAP at {vwap}",
                "target": f"PDL at {pdl}",
            },
        ]

    return [
        {
            "name": "Bullish breakout above ONH",
            "probability": 40,
            "trigger": f"Price breaks above ONH at {onh}. {structure_detail().capitalize()}, {news_detail()}.",
            "invalidation": f"Price falls back below VWAP at {vwap}",
            "target": f"PDH at {pdh}",
        },
        {
            "name": "Bearish breakdown below ONL",
            "probability": 40,
            "trigger": f"Price breaks below ONL at {onl}. {vwap_context()}.",
            "invalidation": f"Price reclaims VWAP at {vwap}",
            "target": f"PDL at {pdl}",
        },
        {
            "name": "Range between ONL and ONH",
            "probability": 20,
            "trigger": f"Price stays inside {onl} to {onh} all session",
            "invalidation": "Any sustained move outside the overnight range",
            "target": f"VWAP at {vwap}",
        },
    ]
