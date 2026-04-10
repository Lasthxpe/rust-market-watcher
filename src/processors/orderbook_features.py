import logging
import json
from datetime import datetime, timezone

import config.config as cfg
from src.utils.strings import make_safe_item_name
from src.utils.math import round_feature

logger = logging.getLogger(__name__)

def get_best_level(orderbook): 
    return orderbook["items"][0]
# ask and bid schemas are the same

def get_spread_abs(best_ask_price, best_bid_price):
    return best_ask_price - best_bid_price

def get_spread_pct(best_ask, best_bid):
    if best_ask["price"] == 0:
        return None
    
    return (best_ask["price"] - best_bid["price"]) / best_ask["price"]

def book_depth_top_n(orderbook, num_levels):
    items = orderbook["items"][:num_levels]
    return sum(item["quantity"] for item in items)

def depth_imbalance_top_n(buy_orderbook, sell_orderbook, num_levels):
    ask_depth = book_depth_top_n(sell_orderbook, num_levels)
    bid_depth = book_depth_top_n(buy_orderbook, num_levels)

    if ask_depth == 0:
        return None
    
    return bid_depth / ask_depth

def gap_to_second_ask_pct(sell_orderbook):
    items = sell_orderbook["items"]

    if len(items) < 2:
        return None
    if items[0]["price"] == 0:
        return None
    
    return (items[1]["price"] - items[0]["price"]) / items[0]["price"]

def largest_wall_top_n(orderbook, num_levels):
    items = orderbook["items"][:num_levels]
    return max(items, key=lambda item: item["quantity"])

def build_orderbook_features(buy_orderbook, sell_orderbook, item_name):

    logger.debug("%s: building orderbook features", item_name)

    best_ask = get_best_level(sell_orderbook)
    best_ask_price = best_ask["price"] / 100
    best_bid = get_best_level(buy_orderbook)
    best_bid_price = best_bid["price"] / 100


    spread_abs = get_spread_abs(best_ask_price, best_bid_price)
    spread_pct = get_spread_pct(best_ask, best_bid)
    second_ask_gap_pct = gap_to_second_ask_pct(sell_orderbook)

    sell_depth_top_5 = book_depth_top_n(sell_orderbook, 5)
    buy_depth_top_5 = book_depth_top_n(buy_orderbook, 5)

    depth_imbalance_top_5 = depth_imbalance_top_n(buy_orderbook, sell_orderbook, 5)

    largest_buy_wall_top_10 = largest_wall_top_n(buy_orderbook, 10)
    largest_buy_wall_top_10_price = largest_buy_wall_top_10["price"] / 100
    largest_sell_wall_top_10 = largest_wall_top_n(sell_orderbook, 10)
    largest_sell_wall_top_10_price = largest_sell_wall_top_10["price"] / 100

    logger.debug("%s: built all orderbook features successfully", item_name)

    return {
    "item_name": item_name,
    "best_bid_price": best_bid_price,
    "best_bid_quantity": best_bid["quantity"],
    "best_ask_price": best_ask_price,
    "best_ask_quantity": best_ask["quantity"],
    "spread_abs": round_feature(spread_abs, 2),
    "spread_pct": round_feature(spread_pct, 4),
    "bid_depth_top_5": buy_depth_top_5,
    "ask_depth_top_5": sell_depth_top_5,
    "depth_imbalance_top_5": round_feature(depth_imbalance_top_5, 4),
    "gap_to_second_ask_pct": round_feature(second_ask_gap_pct, 4),
    "largest_bid_wall_top_10_price": largest_buy_wall_top_10_price,
    "largest_bid_wall_top_10_quantity": largest_buy_wall_top_10["quantity"],
    "largest_ask_wall_top_10_price": largest_sell_wall_top_10_price,
    "largest_ask_wall_top_10_quantity": largest_sell_wall_top_10["quantity"],
}

def save_orderbook_features(buy_orderbook, sell_orderbook, item_name):
    features = build_orderbook_features(buy_orderbook, sell_orderbook, item_name)

    if not isinstance(features, dict):
        return None
    if not features:
        logger.warning("Found 0 features")
        return None

    logger.debug("%s: saving orderbook features", features["item_name"])    

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    save_dir = cfg.ITEM_FEATURES_DIR / timestamp
    save_dir.mkdir(parents=True, exist_ok=True)

    safe_item_name = make_safe_item_name(item_name)

    save_path = save_dir / f"{safe_item_name}-orderbook-features.json"

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(features, f, indent=2)

    logger.info("%s: saved orderbook features to %s", features["item_name"], save_path)

    return save_path

def save_orderbook_features_dataset(features_list):
    if not isinstance(features_list, list):
        raise TypeError("Features_list must be a list")
    if not features_list:
        raise ValueError("Features_list cannot be empty")
    
    logger.debug("Saving aggregated orderbook features dataset (%d items)", len(features_list))

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    save_dir = cfg.ITEM_FEATURES_DIR / timestamp
    save_dir.mkdir(parents=True, exist_ok=True)

    save_path = save_dir / f"orderbook_features_dataset.json"

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(features_list, f, indent=2)

    logger.info("Saved aggregated orderbook features (%d items) to %s", len(features_list), save_path)

    return save_path