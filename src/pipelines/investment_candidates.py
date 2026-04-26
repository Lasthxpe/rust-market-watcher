import json
import logging
from datetime import datetime

import config.config as cfg

logger = logging.getLogger(__name__)


ACTION_GROUP_PRIORITY = {
    "actionable_now": 4,
    "high_priority_watchlist": 3,
    "watchlist": 2,
    "rejected": 1,
}

def save_investment_candidates_dataset(results):
    timestamp = datetime.today().strftime("%Y-%m-%d")

    cfg.INVESTMENT_CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    save_path = cfg.INVESTMENT_CANDIDATES_DIR / f"{timestamp}.json"

    logger.info("Saving investment candidates dataset to %s", save_path)

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info("Saved investment candidates dataset to %s", save_path)

    return save_path


def build_lookup(rows, key="item_name"):
    return {row[key]: row for row in rows}


def calculate_market_score(turnover_row, orderbook_row):
    turnover_score_normalized = turnover_row["turnover_score"] * 5
    liquidity_score = orderbook_row["liquidity_score"]

    market_score = (
        0.35 * turnover_score_normalized
        + 0.65 * liquidity_score
    )

    return round(market_score, 2)


def classify_setup_type(position_row):
    primary_bias = position_row["primary_bias"]
    state = position_row.get("state", [])

    if primary_bias == "avoid_now":
        return "avoid"

    if primary_bias == "accumulation_zone":
        return "accumulation"

    if primary_bias == "watch_for_entry":
        return "recovery_entry"

    if primary_bias == "watch_for_stabilization":
        return "stabilization_setup"

    if "price_discovery" in state:
        return "price_discovery"

    if "near_valid_ath" in state:
        return "ath_watch"

    return "neutral"


def assign_action_group(
    market_score,
    turnover_row,
    position_row,
):
    primary_bias = position_row["primary_bias"]
    state = position_row.get("state", [])

    # hard rejects

    if turnover_row.get("passed_gate") is False:
        return "rejected"

    if market_score < 60:
        return "rejected"

    if primary_bias == "avoid_now":
        return "rejected"

    # never actionable

    if "price_discovery" in state:
        if market_score >= 75:
            return "high_priority_watchlist"
        return "watchlist"

    if "near_valid_ath" in state:
        return "watchlist"

    # actionable setups

    if primary_bias == "accumulation_zone":
        return "actionable_now"

    if primary_bias == "watch_for_entry":
        return "actionable_now"

    if primary_bias == "watch_for_stabilization":
        if market_score >= 70:
            return "actionable_now"
        return "high_priority_watchlist"

    # default

    if market_score >= 70:
        return "high_priority_watchlist"

    return "watchlist"


def build_candidate_reason(result):
    return (
        f"{result['setup_type']} | "
        f"{result['action_group']} | "
        f"score={result['market_score']} | "
        f"bias={result['primary_bias']} | "
        f"state={result['position_state']} | "
        f"flags={result['position_flags']}"
    )


def build_investment_candidates(
    turnover_rows,
    orderbook_rows,
    position_rows,
):
    turnover_by_name = build_lookup(turnover_rows)
    orderbook_by_name = build_lookup(orderbook_rows)

    flat_results = []

    for position_row in position_rows:
        item_name = position_row["item_name"]

        turnover_row = turnover_by_name.get(item_name)
        orderbook_row = orderbook_by_name.get(item_name)

        if turnover_row is None or orderbook_row is None:
            logger.warning(
                "Skipping %s because matching turnover/orderbook row is missing",
                item_name
            )
            continue

        market_score = calculate_market_score(
            turnover_row,
            orderbook_row
        )

        setup_type = classify_setup_type(position_row)

        action_group = assign_action_group(
            market_score,
            turnover_row,
            position_row,
        )

        result = {
            "item_name": item_name,

            "setup_type": setup_type,
            "action_group": action_group,

            "market_score": market_score,

            "turnover_score": turnover_row["turnover_score"],
            "turnover_score_normalized": turnover_row["turnover_score"] * 5,
            "turnover_label": turnover_row.get("turnover_label"),
            "turnover_passed_gate": turnover_row.get("passed_gate"),
            "turnover_flags": turnover_row.get("flags", []),

            "orderbook_liquidity_score": orderbook_row["liquidity_score"],
            "orderbook_liquidity_label": orderbook_row.get("liquidity_label"),
            "orderbook_flags": orderbook_row.get("flags", []),

            "primary_bias": position_row["primary_bias"],
            "position_state": position_row.get("state", []),
            "position_flags": position_row.get("flags", []),

            "absolute_position_range": position_row.get(
                "absolute_position_range"
            ),
            "structural_position_range": position_row.get(
                "structural_position_range"
            ),

            "latest_price": position_row.get("latest_price"),
            "raw_ath_365d": position_row.get("raw_ath_365d"),
            "raw_atl_365d": position_row.get("raw_atl_365d"),
            "valid_ath_365d": position_row.get("valid_ath_365d"),
            "valid_atl_365d": position_row.get("valid_atl_365d"),
            "history_length": position_row.get("history_length"),
        }

        result["candidate_reason"] = build_candidate_reason(result)

        flat_results.append(result)

    flat_results.sort(
        key=lambda row: (
            ACTION_GROUP_PRIORITY[row["action_group"]],
            row["market_score"],
        ),
        reverse=True,
    )

    grouped_results = {
        "actionable_now": [],
        "high_priority_watchlist": [],
        "watchlist": [],
        "rejected": [],
    }

    for result in flat_results:
        grouped_results[result["action_group"]].append(result)

    return grouped_results