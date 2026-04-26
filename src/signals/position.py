import json
import logging
from datetime import datetime

import config.config as cfg

logger = logging.getLogger(__name__)

# extract inputs
def load_price_history_context(item_name, days=365):
    path = cfg.FULL_PRICE_HISTORY_DIR / f"{item_name}.json"

    with open(path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    n = min(len(rows), days)

    return {
        "recent_rows": rows[-n:],
        "total_history_length": len(rows),
        "recent_history_length": n,
    }

def extract_position_inputs(features_row):
    item_name = features_row["item_name"]

    history_context = load_price_history_context(item_name)
    recent_history = history_context["recent_rows"]
    total_history_length = history_context["total_history_length"]

    valid_rows = [row for row in recent_history if row["volume"] >= 3]

    if not valid_rows:
        valid_rows = recent_history

    prices = sorted(row["median"] for row in valid_rows)

    raw_ath_365d = max(prices)
    raw_atl_365d = min(prices)

    low_index = int(len(prices) * 0.05)
    high_index = int((len(prices) - 1) * 0.95)

    valid_atl_365d = prices[low_index]
    valid_ath_365d = prices[high_index]

    latest_price = features_row["latest_price"]

    last_90_rows = recent_history[-90:]
    prices_90d = [row["median"] for row in last_90_rows]
    range_90d_pct = (max(prices_90d) - min(prices_90d)) / latest_price

    return {
        "item_name": item_name,
        "latest_price": features_row["latest_price"],
        "return_7d_pct": features_row["return_7d_pct"],
        "return_30d_pct": features_row["return_30d_pct"],
        "range_90d_pct": range_90d_pct,
        "raw_ath_365d": raw_ath_365d,
        "raw_atl_365d": raw_atl_365d,
        "valid_ath_365d": valid_ath_365d,
        "valid_atl_365d": valid_atl_365d,
        "total_history_length": total_history_length,
        "recent_history_length": len(recent_history),
    }


# derive context
def derive_position_context(inputs):

    item_name = inputs["item_name"]
    latest_price = inputs["latest_price"]
    return_7d_pct = inputs["return_7d_pct"]
    return_30d_pct = inputs["return_30d_pct"]
    raw_ath_365d = inputs["raw_ath_365d"]
    raw_atl_365d = inputs["raw_atl_365d"]
    valid_ath_365d = inputs["valid_ath_365d"]
    valid_atl_365d = inputs["valid_atl_365d"]
    range_90d_pct = inputs["range_90d_pct"]
    total_history_length = inputs["total_history_length"]

    state = []
    flags = []
    decision_bias = []
    primary_bias = None

    if (raw_ath_365d - raw_atl_365d) == 0 or (valid_ath_365d - valid_atl_365d) == 0:
        return {
            "item_name": item_name,
            "state": ["flat_range"],
            "flags": ["no_price_variation"],
            "primary_bias": "avoid_now",
            "decision_bias": ["avoid"],
        }


    absolute_position_range = (latest_price - raw_atl_365d) / (raw_ath_365d - raw_atl_365d)
    structural_position_range = (latest_price - valid_atl_365d) / (valid_ath_365d - valid_atl_365d)

    # near bottom
    if structural_position_range < 0:
        state.append("below_structural_floor")
    elif structural_position_range <= 0.2:
        state.append("near_valid_atl")
    # near top
    elif structural_position_range > 1:
        state.append("price_discovery")
    elif structural_position_range >= 0.8:
        state.append("near_valid_ath")

    # boring middle
    elif 0.4 <= structural_position_range <= 0.6:
        state.append("middle_range")
    elif 0.2 < structural_position_range < 0.4:
        state.append("lower_mid_range")
    elif 0.6 < structural_position_range < 0.8:
        state.append("upper_mid_range")
        
    if total_history_length < 180:
        state.append("first_cycle")


    if return_7d_pct > 3 and return_30d_pct > 5:
        flags.append("uptrend")

    if "near_valid_atl" in state and return_7d_pct > 5 and return_30d_pct >= 3:
        flags.append("recovering_from_bottom")

    if absolute_position_range <= 0.4 and return_7d_pct >= 5 and return_30d_pct <= 0:
        flags.append("early_recovery")

    if "near_valid_ath" in state and return_7d_pct > 7 and return_30d_pct > 15:
        flags.append("overextended")

    if absolute_position_range >= 0.6 and return_7d_pct > 20:
        flags.append("active_pump")

    if "near_valid_ath" in state and "uptrend" in flags and "active_pump" not in flags and "overextended" not in flags:
        flags.append("high_range_strength")


    if return_7d_pct < -3 and return_30d_pct < -5:
        flags.append("downtrend")

    if return_7d_pct < -10 and return_30d_pct < -10:
        flags.append("falling_knife")
    elif return_7d_pct < -5 and return_30d_pct < 0:
        flags.append("weak_decline")

    if return_7d_pct < -20:
        flags.append("sharp_dump")

    if absolute_position_range >= 0.6 and return_7d_pct < -5 and return_30d_pct > 0:
        flags.append("pullback_from_high")

    if absolute_position_range >= 0.6 and return_7d_pct < -5 and return_30d_pct < 0:
        flags.append("high_range_breakdown")

    if return_7d_pct < 0 and return_30d_pct > 0:
        flags.append("short_term_weakness")


    if range_90d_pct <= 0.25 and abs(return_30d_pct) < 10:
        flags.append("consolidating")


    # primary bias

    if "falling_knife" in flags:
        primary_bias = "avoid_now"

    elif "high_range_breakdown" in flags:
        primary_bias = "avoid_now"

    elif "active_pump" in flags:
        primary_bias = "avoid_now"


    # special structural states

    elif "price_discovery" in state and "short_term_weakness" in flags:
        primary_bias = "watch_breakout_retest"

    elif "price_discovery" in state and "uptrend" in flags:
        primary_bias = "monitor_breakout"

    elif "below_structural_floor" in state and "downtrend" in flags:
        primary_bias = "avoid_now"

    elif "below_structural_floor" in state:
        primary_bias = "watch_for_reclaim"


    # normal high-range logic

    elif "overextended" in flags:
        primary_bias = "avoid_now"

    elif "near_valid_ath" in state and "high_range_strength" in flags:
        primary_bias = "portfolio_anchor_candidate"

    elif "near_valid_ath" in state:
        primary_bias = "wait_for_pullback"


    # entry logic

    elif "recovering_from_bottom" in flags:
        primary_bias = "watch_for_entry"

    elif "early_recovery" in flags:
        primary_bias = "watch_for_entry"

    elif "near_valid_atl" in state and "consolidating" in flags:
        primary_bias = "accumulation_zone"

    elif "near_valid_atl" in state and "short_term_weakness" in flags:
        primary_bias = "watch_for_stabilization"


    # neutral-trend logic

    elif "consolidating" in flags:
        primary_bias = "monitor_consolidation"

    elif "uptrend" in flags:
        primary_bias = "monitor_trend"

    else:
        primary_bias = "neutral"

    return {
        "item_name": item_name,
        "state": state,
        "flags": flags,
        "primary_bias": primary_bias,
        "decision_bias": decision_bias,
        "absolute_position_range": round(absolute_position_range, 4),
        "structural_position_range": round(structural_position_range, 4),
        "latest_price": latest_price,
        "raw_ath_365d": raw_ath_365d,
        "raw_atl_365d": raw_atl_365d,
        "valid_ath_365d": valid_ath_365d,
        "valid_atl_365d": valid_atl_365d,
        "history_length": total_history_length,
    }
    
def evaluate_position_context(features_rows):
    logger.info("Starting position context evaluation for %d items", len(features_rows))

    results = []

    for row in features_rows:
        item_name = row.get("item_name", "<unknown>")

        try:
            inputs = extract_position_inputs(row)
            context = derive_position_context(inputs)
            results.append(context)

        except Exception:
            logger.exception("Failed to evaluate position context for item: %s", item_name)

    logger.info("Finished position context evaluation. Processed %d items", len(results))

    return results    

def save_position_context_dataset(results):
    timestamp = datetime.today().strftime("%Y-%m-%d")

    cfg.POSITION_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    save_path = cfg.POSITION_CONTEXT_DIR / f"{timestamp}.json"

    logger.info("Saving position context dataset to %s", save_path)

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info("Saved position context dataset with %d items", len(results))

    return save_path

