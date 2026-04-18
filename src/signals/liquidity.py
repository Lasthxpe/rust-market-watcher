from datetime import datetime
import json

import config.config as cfg

def check_liquidity_gate(row):
    if row["average_volume_30d"] < 25:
        return {
            "item_name": row["item_name"],
            "passed_gate": False,
            "score": 0.0,
            "label": "failed_gate",
            "flags": ["failed_liquidity_gate"],
            "reasons": ["30d volume is below the minimum threshold of 25"]
        }
    
    return None

def assign_liquidity_strength_bucket(row):
    score = 0
    average_30d = row["average_volume_30d"]

    if 25 <= average_30d < 40:
        bucket = "weak"
        score += 8
    elif 40 <= average_30d < 60:
        bucket = "acceptable"
        score += 11
    elif 60 <= average_30d < 90:
        bucket = "strong"
        score += 14
    elif average_30d >= 90:
        bucket = "elite"
        score +=16

    return bucket, score

def assign_liquidity_trend_bucket(row):
    ratio_7d_vs_30d = row["average_volume_7d"] / row["average_volume_30d"]
    score = 0

    if ratio_7d_vs_30d >= 1.25:
        volume_trend = "improving_fast"
        score += 4
    elif 1.05 < ratio_7d_vs_30d < 1.25:
        volume_trend = "improving"
        score += 2
    elif 0.95 <= ratio_7d_vs_30d <= 1.05:
        volume_trend = "stable"
        score += 1
    elif 0.85 <= ratio_7d_vs_30d < 0.95:
        volume_trend = "weakening"
        score += -2
    elif ratio_7d_vs_30d < 0.85:
        volume_trend = "weakening_fast"
        score += -3

    return volume_trend, score

def score_liquidity(rows):

    scored_items = []

    strength_flags = {
        "weak": "weak_30d_liquidity",
        "acceptable": "acceptable_30d_liquidity",
        "strong": "strong_30d_liquidity",
        "elite": "elite_30d_liquidity",
    }

    trend_flags = {
        "improving_fast": "liquidity_improving_fast",
        "improving": "liquidity_improving",
        "stable": "liquidity_stable",
        "weakening": "liquidity_weakening",
        "weakening_fast": "liquidity_weakening_fast",
    }

    strength_reasons = {
        "weak": "30d average volume is above the minimum threshold but still relatively weak",
        "acceptable": "30d average volume is acceptable for tradability",
        "strong": "30d average volume is strong enough for reliable execution",
        "elite": "30d average volume is elite and supports highly tradable execution",
    }

    trend_reasons = {
        "improving_fast": "7d average volume is improving fast relative to the 30d baseline",
        "improving": "7d average volume is improving relative to the 30d baseline",
        "stable": "7d average volume is stable relative to the 30d baseline",
        "weakening": "7d average volume is weakening relative to the 30d baseline",
        "weakening_fast": "7d average volume is falling materially below the 30d baseline",
    }

    for row in rows:

        gate_result = check_liquidity_gate(row)

        if gate_result is not None:
            scored_items.append(gate_result)
            continue
        
        trend_bucket, trend_score = assign_liquidity_trend_bucket(row)
        strength_bucket, base_score = assign_liquidity_strength_bucket(row)

        strength_flag = strength_flags[strength_bucket]
        trend_flag = trend_flags[trend_bucket]

        strength_reason = strength_reasons[strength_bucket]
        trend_reason = trend_reasons[trend_bucket]

        final_score = base_score + trend_score
        final_score = max(0, min(20, final_score))

        result = {
            "item_name": row["item_name"],
            "passed_gate": True,
            "score": final_score,
            "label": strength_bucket,
            "flags": [strength_flag, trend_flag],
            "reasons": [strength_reason, trend_reason],
            "base_score": base_score,
            "trend_score": trend_score,
            "strength_bucket": strength_bucket,
            "trend_bucket":  trend_bucket,
        }

        scored_items.append(result)
        
    scored_items = sorted(scored_items, key=lambda x: x["score"], reverse=True)

    return scored_items

def save_liquidity_scores_dataset(scored_items):
    timestamp = datetime.today().strftime("%Y-%m-%d")

    cfg.LIQUIDITY_SCORES.mkdir(parents=True, exist_ok=True)
    save_path = cfg.LIQUIDITY_SCORES / f"{timestamp}.json"

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(scored_items, f, indent=2)

    return save_path