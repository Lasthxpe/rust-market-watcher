from datetime import datetime
import json
import logging

import config.config as cfg

logger = logging.getLogger(__name__)

def extract_liquidity_inputs(features_row):

    required_keys = [
    "spread_abs",
    "spread_pct",
    "best_bid_size",
    "best_ask_size",
    "bid_depth_top_5",
    "ask_depth_top_5",
    "bid_depth_top_10",
    "ask_depth_top_10",
    ]

    inputs = {}

    for key in required_keys:
        if key not in features_row:
            raise ValueError(f"Missing required feature: {key}")
        
        value = features_row[key]

        try:
            inputs[key] = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid value for {key}: {value}")

    return inputs

def score_within_band(spread, band_start, band_end, best_score, worst_score):
        
        position = (spread - band_start) / (band_end - band_start)
        score = best_score - position * (best_score - worst_score)    

        return score, position

def score_tightness(inputs):

    spread_pct = inputs["spread_pct"]

    tightness_score = 0.0
    tightness_label = None
    flags = []

    if spread_pct < 0.13:
        tightness_label = "excellent"
        tightness_score, position = score_within_band(
            spread=spread_pct,
            band_start=0.0,
            band_end=0.13,
            best_score=100,
            worst_score=90
        )

        flags.append("sub_fee_spread")

        if position >= 0.8:
            flags.append("near_worse_band")

    elif 0.13 <= spread_pct < 0.18:
        tightness_label = "good"
        tightness_score, position = score_within_band(
            spread=spread_pct,
            band_start=0.13,
            band_end=0.18,
            best_score=90,
            worst_score=75
        )
        
        flags.append("healthy_spread")

        if position <= 0.2:
            flags.append("near_better_band")
        elif position >= 0.8:
            flags.append("near_worse_band")

    elif 0.18 <= spread_pct < 0.22:
        tightness_label = "acceptable"
        tightness_score, position = score_within_band(
            spread=spread_pct,
            band_start=0.18,
            band_end=0.22,
            best_score=75,
            worst_score=55
        )

        flags.append("acceptable_spread")

        if position <= 0.2:
            flags.append("near_better_band")
        elif position >= 0.8:
            flags.append("near_worse_band")

    elif 0.22 <= spread_pct < 0.3:
        tightness_label = "weak"
        tightness_score, position = score_within_band(
            spread=spread_pct,
            band_start=0.22,
            band_end=0.3,
            best_score=55,
            worst_score=30
        )

        flags.append("wide_spread")

        if position <= 0.2:
            flags.append("near_better_band")
        elif position >= 0.8:
            flags.append("near_worse_band")

    else:
        tightness_label = "poor"
        tightness_score = 0.0

        flags.append("very_wide_spread")

    return {
        "tightness_score": round(tightness_score, 2),
        "tightness_label": tightness_label,
        "flags": flags,
    }

def score_touch(inputs):
    best_bid_size = inputs["best_bid_size"]
    best_ask_size = inputs["best_ask_size"]
    bid_depth_top_5 = inputs["bid_depth_top_5"]
    ask_depth_top_5 = inputs["ask_depth_top_5"]
    bid_depth_top_10 = inputs["bid_depth_top_10"]
    ask_depth_top_10 = inputs["ask_depth_top_10"]

    touch_score = 0.0
    touch_label = None
    flags = []

    weaker_best_size = min(best_bid_size, best_ask_size) # orderbook's only as strong as its weakest side
    avg_best_size = (best_bid_size + best_ask_size) / 2

    weaker_top5_depth = min(bid_depth_top_5, ask_depth_top_5) # orderbook's only as strong as its weakest side
    avg_top5_depth = (bid_depth_top_5 + ask_depth_top_5) / 2

    weaker_top10_depth = min(bid_depth_top_10, ask_depth_top_10)


    weaker_best_size_score = 0.0

    if weaker_best_size <= 1:
        weaker_best_size_score = 35
    elif weaker_best_size <= 3:
        weaker_best_size_score = 55
    elif weaker_best_size <= 7:
        weaker_best_size_score = 75
    else:
        weaker_best_size_score = 90


    avg_best_size_score = 0.0

    if avg_best_size < 2:
        avg_best_size_score = 35
    elif avg_best_size < 4:
        avg_best_size_score = 55
    elif avg_best_size < 8:
        avg_best_size_score = 75
    else:
        avg_best_size_score = 90


    weaker_top5_depth_score = 0.0

    if weaker_top5_depth < 5:
        weaker_top5_depth_score = 15
    elif weaker_top5_depth < 12:
        weaker_top5_depth_score = 60
    elif weaker_top5_depth < 30:
        weaker_top5_depth_score = 80
    else:
        weaker_top5_depth_score = 90


    avg_top5_depth_score = 0.0

    if avg_top5_depth < 8:
        avg_top5_depth_score = 20
    elif avg_top5_depth < 18:
        avg_top5_depth_score = 50
    elif avg_top5_depth < 35:
        avg_top5_depth_score = 75
    else:
        avg_top5_depth_score = 90

    touch_score = (
        0.2 * weaker_best_size_score + 
        0.05 * avg_best_size_score + 
        0.6 * weaker_top5_depth_score + 
        0.15 * avg_top5_depth_score
    )

    if touch_score >= 80:
        touch_label = "strong"
    elif touch_score >= 65:
        touch_label = "good"
    elif touch_score >= 50:
        touch_label = "acceptable"
    elif touch_score >= 30:
        touch_label = "weak"
    else: 
        touch_label = "poor"


    if best_bid_size == 1:
        flags.append("single_unit_best_bid")

    if best_ask_size == 1:
        flags.append("single_unit_best_ask")

    if weaker_top5_depth < 5:
        flags.append("weak_nearby_support")
    elif weaker_top5_depth < 12:
        flags.append("moderate_nearby_support")
    else:
        flags.append("strong_nearby_support")

    if weaker_best_size <= 1:
        if weaker_top5_depth >= 12:
            flags.append("thin_top_but_supported")
        else:
            flags.append("thin_top_and_weak_support")
    elif weaker_best_size >= 4 and weaker_top5_depth >= 12:
        flags.append("solid_top_and_supported")

    if weaker_top10_depth <= weaker_top5_depth * 1.3:
        flags.append("shallow_extension")
    elif weaker_top10_depth >= weaker_top5_depth * 2:
        flags.append("deep_extension")

    if weaker_best_size > 0:
        best_size_ratio = max(best_bid_size, best_ask_size) / weaker_best_size
        if best_size_ratio >= 2:
            flags.append("touch_asymmetry")

    return {
        "touch_score": round(touch_score, 2),
        "touch_label": touch_label,
        "flags": flags,
        "weaker_best_size_score": weaker_best_size_score,
        "avg_best_size_score": avg_best_size_score,
        "weaker_top5_depth_score": weaker_top5_depth_score,
        "avg_top5_depth_score": avg_top5_depth_score,
    }

def evaluate_orderbook_liquidity(features_rows):

    logger.info("Starting orderbook liquidity evaluation for %d items", len(features_rows))

    scored_items = []

    for row in features_rows:

        try:
            inputs = extract_liquidity_inputs(row)
            tightness = score_tightness(inputs)
            touch = score_touch(inputs)
        
            liquidity_score = (
                0.5 * tightness["tightness_score"] + 
                0.5 * touch["touch_score"]
            )

            liquidity_label = None

            if liquidity_score >= 80:
                liquidity_label = "strong"
            elif liquidity_score >= 65:
                liquidity_label = "good"
            elif liquidity_score >= 50:
                liquidity_label = "acceptable"
            elif liquidity_score >= 30:
                liquidity_label = "weak"
            else:
                liquidity_label = "poor"

            flags = tightness["flags"] + touch["flags"]

            result = {
                "item_name": row["item_name"],
                "liquidity_score": round(liquidity_score, 2),
                "liquidity_label": liquidity_label,
                "tightness": tightness,
                "touch": touch,
                "flags": flags
            }

            scored_items.append(result)

        except Exception:
            item_name = row.get("item_name", "<unknown>")
            logger.exception("Failed to evaluate orderbook liquidity for item: %s", item_name)

    scored_items = sorted(scored_items, key=lambda x: x["liquidity_score"], reverse=True)

    logger.info("Finished orderbook liquidity evaluation. Scored %d items", len(scored_items))

    return scored_items

def save_orderbook_liquidity_scores_dataset(scored_items):
    timestamp = datetime.today().strftime("%Y-%m-%d")

    cfg.ORDERBOOK_LIQUIDITY_SCORES_DIR.mkdir(parents=True, exist_ok=True)
    save_path = cfg.ORDERBOOK_LIQUIDITY_SCORES_DIR / f"{timestamp}.json"

    logger.info("Saving orderbook liquidity scores dataset to %s", save_path)

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(scored_items, f, indent=2)

    logger.info("Saved orderbook liquidity scores dataset with %d items", len(scored_items))

    return save_path