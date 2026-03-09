def get_scenarios(primary_bias: str, snapshot: dict) -> list:
    """
    Returns exactly 3 scenarios. Each scenario has:
    - name, probability, trigger, invalidation, target, reasons
    reasons is a list of 2-3 short strings explaining why this scenario is valid.
    """
    onh  = snapshot["onh"]
    onl  = snapshot["onl"]
    pdh  = snapshot["pdh"]
    pdl  = snapshot["pdl"]
    vwap = snapshot["vwap"]

    sweep            = snapshot["sweep_detected_preopen"]
    news_bias        = snapshot["news_bias"]
    above_vwap       = snapshot["above_or_below_vwap"] == "above"
    holds_vwap       = snapshot["holds_vwap"]
    structure        = snapshot["premarket_structure"]
    compression      = snapshot["compression_before_open"]
    expansion_score  = snapshot["expansion_score"]
    directional_score = snapshot["directional_score"]

    # --- reason helpers ---
    def structure_reason():
        if structure == "higher_highs":
            return "Premarket is printing higher highs"
        if structure == "lower_lows":
            return "Premarket is printing lower lows"
        if structure == "sweep_and_reverse":
            return "Premarket swept a level and reversed"
        if structure == "consolidation":
            return "Premarket is consolidating — no directional edge"
        return "Premarket is ranging"

    def vwap_reason():
        if holds_vwap and above_vwap:
            return f"Price is holding above VWAP at {vwap}"
        if not holds_vwap and not above_vwap:
            return f"Price is failing below VWAP at {vwap}"
        return f"VWAP at {vwap} is the key pivot level"

    def news_reason():
        if news_bias == "bullish":
            return "News bias supports upside"
        if news_bias == "bearish":
            return "News bias supports downside"
        return "News bias is neutral — no macro edge"

    def expansion_reason():
        if expansion_score >= 7:
            return f"High expansion score ({expansion_score}) — strong move expected"
        if expansion_score <= 3:
            return f"Low expansion score ({expansion_score}) — limited range expected"
        return f"Moderate expansion score ({expansion_score})"

    def directional_reason():
        if directional_score >= 7:
            return f"High directional score ({directional_score}) — clear bias"
        if directional_score <= 3:
            return f"Low directional score ({directional_score}) — no clear bias"
        return f"Mixed directional score ({directional_score})"

    def compression_reason():
        if compression:
            return "Compression before open increases breakout probability"
        return "No compression — open may be choppy"

    def sweep_reason():
        return "Sweep detected preopen — liquidity already taken"

    # --- sweep/reversal scenarios ---
    sweep_reversal_bullish = {
        "name": "Post-sweep bullish reversal",
        "probability": 25,
        "trigger": f"Sweep below ONL at {onl} already occurred — look for reclaim and reversal above {onl}",
        "invalidation": f"Price continues lower below {pdl}",
        "target": f"ONH at {onh} after reclaim of VWAP at {vwap}",
        "reasons": [
            sweep_reason(),
            vwap_reason(),
            compression_reason(),
        ],
    }

    sweep_reversal_bearish = {
        "name": "Post-sweep bearish reversal",
        "probability": 25,
        "trigger": f"Sweep above ONH at {onh} already occurred — look for rejection and reversal below {onh}",
        "invalidation": f"Price continues higher above {pdh}",
        "target": f"ONL at {onl} after break below VWAP at {vwap}",
        "reasons": [
            sweep_reason(),
            vwap_reason(),
            compression_reason(),
        ],
    }

    # --- BULLISH primary ---
    if primary_bias == "bullish":
        scenario_1 = {
            "name": "Bullish continuation above ONH",
            "probability": 60,
            "trigger": f"Price reclaims and holds above ONH at {onh}",
            "invalidation": f"Price fails back below VWAP at {vwap} on a closing basis",
            "target": f"PDH at {pdh}",
            "reasons": [
                structure_reason(),
                vwap_reason(),
                news_reason(),
            ],
        }
        scenario_2 = sweep_reversal_bearish if sweep else {
            "name": "Rejection at ONH — fade back to discount",
            "probability": 25,
            "trigger": f"Price spikes into ONH at {onh} and shows a reversal candle or exhaustion",
            "invalidation": f"Sustained break and close above {onh}",
            "target": f"ONL at {onl}",
            "reasons": [
                expansion_reason(),
                f"ONH at {onh} is a premium — expect profit taking",
                news_reason(),
            ],
        }
        scenario_3 = {
            "name": "Range between ONL and ONH",
            "probability": 15,
            "trigger": f"Price stays between {onl} and {onh} with no clear breakout",
            "invalidation": f"Clean breakout above {onh} or below {onl}",
            "target": f"VWAP at {vwap}",
            "reasons": [
                directional_reason(),
                compression_reason(),
                f"ONL at {onl} and ONH at {onh} act as hard boundaries",
            ],
        }
        return [scenario_1, scenario_2, scenario_3]

    # --- BEARISH primary ---
    if primary_bias == "bearish":
        scenario_1 = {
            "name": "Bearish continuation below ONL",
            "probability": 60,
            "trigger": f"Price breaks and holds below ONL at {onl}",
            "invalidation": f"Price reclaims VWAP at {vwap} and holds above it",
            "target": f"PDL at {pdl}",
            "reasons": [
                structure_reason(),
                vwap_reason(),
                news_reason(),
            ],
        }
        scenario_2 = sweep_reversal_bullish if sweep else {
            "name": "Bullish reclaim of VWAP",
            "probability": 25,
            "trigger": f"Price drives up through VWAP at {vwap} with momentum and holds",
            "invalidation": f"Price fails back below ONL at {onl}",
            "target": f"ONH at {onh}",
            "reasons": [
                expansion_reason(),
                f"VWAP at {vwap} is a key reclaim level for bulls",
                news_reason(),
            ],
        }
        scenario_3 = {
            "name": "Range between ONL and VWAP",
            "probability": 15,
            "trigger": f"Price oscillates between {onl} and {vwap} with no expansion",
            "invalidation": f"Clean break below {onl} or above {vwap}",
            "target": f"Midpoint at {round((onl + vwap) / 2, 2)}",
            "reasons": [
                directional_reason(),
                compression_reason(),
                f"VWAP at {vwap} and ONL at {onl} cap both sides",
            ],
        }
        return [scenario_1, scenario_2, scenario_3]

    # --- NEUTRAL primary ---
    if sweep:
        return [
            {
                "name": "Post-sweep reversal play",
                "probability": 45,
                "trigger": f"Look for reversal after reclaim of ONH at {onh} or ONL at {onl}",
                "invalidation": f"Price extends beyond {pdh} or {pdl} without reversal",
                "target": f"VWAP at {vwap}",
                "reasons": [
                    sweep_reason(),
                    compression_reason(),
                    vwap_reason(),
                ],
            },
            {
                "name": "Bullish breakout above ONH",
                "probability": 30,
                "trigger": f"Price breaks above ONH at {onh} with momentum",
                "invalidation": f"Price falls back below VWAP at {vwap}",
                "target": f"PDH at {pdh}",
                "reasons": [
                    news_reason(),
                    expansion_reason(),
                    structure_reason(),
                ],
            },
            {
                "name": "Bearish breakdown below ONL",
                "probability": 25,
                "trigger": f"Price breaks below ONL at {onl} and holds",
                "invalidation": f"Price reclaims VWAP at {vwap}",
                "target": f"PDL at {pdl}",
                "reasons": [
                    vwap_reason(),
                    news_reason(),
                    directional_reason(),
                ],
            },
        ]

    # --- NEUTRAL, no sweep ---
    return [
        {
            "name": "Bullish breakout above ONH",
            "probability": 40,
            "trigger": f"Price breaks above ONH at {onh} with momentum",
            "invalidation": f"Price falls back below VWAP at {vwap}",
            "target": f"PDH at {pdh}",
            "reasons": [
                structure_reason(),
                news_reason(),
                expansion_reason(),
            ],
        },
        {
            "name": "Bearish breakdown below ONL",
            "probability": 40,
            "trigger": f"Price breaks below ONL at {onl} and holds",
            "invalidation": f"Price reclaims VWAP at {vwap}",
            "target": f"PDL at {pdl}",
            "reasons": [
                vwap_reason(),
                news_reason(),
                directional_reason(),
            ],
        },
        {
            "name": "Range between ONL and ONH",
            "probability": 20,
            "trigger": f"Price stays inside {onl} to {onh} all session",
            "invalidation": "Any sustained move outside the overnight range",
            "target": f"VWAP at {vwap}",
            "reasons": [
                directional_reason(),
                compression_reason(),
                f"ONL at {onl} and ONH at {onh} act as hard boundaries",
            ],
        },
    ]
