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

def get_best_level_imbalance(best_ask_size, best_bid_size):
    if (best_bid_size + best_ask_size) == 0:
        return None

    return (best_bid_size - best_ask_size) / (best_bid_size + best_ask_size)

def get_spread_abs(best_ask_price, best_bid_price):
    return best_ask_price - best_bid_price

def get_spread_pct(best_ask, best_bid):
    if best_ask["price"] == 0:
        return None
    
    return (best_ask["price"] - best_bid["price"]) / best_ask["price"]

def book_depth_top_n(orderbook, num_levels):
    items = orderbook["items"][:num_levels]
    return sum(item["quantity"] for item in items)

def depth_imbalance_top_n(bid_orderbook, ask_orderbook, num_levels):
    ask_depth = book_depth_top_n(ask_orderbook, num_levels)
    bid_depth = book_depth_top_n(bid_orderbook, num_levels)

    if ask_depth == 0:
        return None
    
    return bid_depth / ask_depth

def gap_to_second_ask_pct(ask_orderbook):
    items = ask_orderbook["items"]

    if len(items) < 2:
        return None
    if items[0]["price"] == 0:
        return None
    
    return (items[1]["price"] - items[0]["price"]) / items[0]["price"]

def gap_to_second_bid_pct(bid_orderbook):
    items = bid_orderbook["items"]

    if len(items) < 2:
        return None
    if items[0]["price"] == 0:
        return None
    
    return (items[0]["price"] - items[1]["price"]) / items[0]["price"]

def largest_wall_top_n(orderbook, num_levels):
    items = orderbook["items"][:num_levels]

    if not items:
        return None
    
    return max(items, key=lambda item: item["quantity"])

def largest_wall_share(book_depth, largest_wall):
    if book_depth == 0:
        return None
    
    return largest_wall["quantity"] / book_depth

def best_level_share(best_level_size, depth_top_n):
    if depth_top_n == 0:
        return None
    
    return best_level_size / depth_top_n

def build_orderbook_features(bid_orderbook, ask_orderbook, item_name):

    logger.debug("%s: building orderbook features", item_name)

    best_ask = get_best_level(ask_orderbook)
    best_ask_price = best_ask["price"] / 100
    best_ask_size = best_ask["quantity"]
    best_bid = get_best_level(bid_orderbook)
    best_bid_price = best_bid["price"] / 100
    best_bid_size = best_bid["quantity"]

    spread_abs = get_spread_abs(best_ask_price, best_bid_price)
    spread_pct = get_spread_pct(best_ask, best_bid)

    second_ask_gap_pct = gap_to_second_ask_pct(ask_orderbook)
    second_bid_gap_pct = gap_to_second_bid_pct(bid_orderbook)

    ask_depth_top_5 = book_depth_top_n(ask_orderbook, 5)
    ask_depth_top_10 = book_depth_top_n(ask_orderbook, 10)
    bid_depth_top_5 = book_depth_top_n(bid_orderbook, 5)
    bid_depth_top_10 = book_depth_top_n(bid_orderbook, 10)

    best_bid_share_top_5 = best_level_share(best_bid_size, bid_depth_top_5)
    best_ask_share_top_5 = best_level_share(best_ask_size, ask_depth_top_5)

    depth_imbalance_top_5 = depth_imbalance_top_n(bid_orderbook, ask_orderbook, 5)
    depth_imbalance_top_10 = depth_imbalance_top_n(bid_orderbook, ask_orderbook, 10)

    best_level_imbalance = get_best_level_imbalance(best_ask_size, best_bid_size)

    largest_bid_wall_top_10 = largest_wall_top_n(bid_orderbook, 10)
    largest_bid_wall_top_10_price = largest_bid_wall_top_10["price"] / 100
    largest_ask_wall_top_10 = largest_wall_top_n(ask_orderbook, 10)
    largest_ask_wall_top_10_price = largest_ask_wall_top_10["price"] / 100

    largest_bid_wall_share_top_10 = largest_wall_share(bid_depth_top_10, largest_bid_wall_top_10)
    largest_ask_wall_share_top_10 = largest_wall_share(ask_depth_top_10, largest_ask_wall_top_10)

    largest_bid_wall_distance_from_best_bid_pct = (best_bid_price - largest_bid_wall_top_10_price) / best_bid_price
    largest_ask_wall_distance_from_best_ask_pct = (largest_ask_wall_top_10_price - best_ask_price) / best_ask_price

    logger.debug("%s: built all orderbook features successfully", item_name)

    return {
    "item_name": item_name,

    # touch / best levels
    "best_bid_price": best_bid_price,
    "best_bid_size": best_bid_size,
    "best_ask_price": best_ask_price,
    "best_ask_size": best_ask_size,

    # spread
    "spread_abs": round_feature(spread_abs, 2),
    "spread_pct": round_feature(spread_pct, 4),

    # level-to-level fragility
    "gap_to_second_ask_pct": round_feature(second_ask_gap_pct, 4),
    "gap_to_second_bid_pct": round_feature(second_bid_gap_pct, 4),

    # depth
    "bid_depth_top_5": bid_depth_top_5,
    "ask_depth_top_5": ask_depth_top_5,
    "bid_depth_top_10": bid_depth_top_10,
    "ask_depth_top_10": ask_depth_top_10,

    # concentration near touch
    "best_bid_share_top_5": round_feature(best_bid_share_top_5, 4),
    "best_ask_share_top_5": round_feature(best_ask_share_top_5, 4),

    # imbalance
    "depth_imbalance_top_5": round_feature(depth_imbalance_top_5, 4),
    "depth_imbalance_top_10": round_feature(depth_imbalance_top_10, 4),

    # best level pressure
    "best_level_imbalance": round_feature(best_level_imbalance, 2),

    # walls
    "largest_bid_wall_top_10_price": largest_bid_wall_top_10_price,
    "largest_bid_wall_top_10_size": largest_bid_wall_top_10["quantity"],
    "largest_ask_wall_top_10_price": largest_ask_wall_top_10_price,
    "largest_ask_wall_top_10_size": largest_ask_wall_top_10["quantity"],

    # walls relative to total visible depth
    "largest_bid_wall_share_top_10": round_feature(largest_bid_wall_share_top_10, 4),
    "largest_ask_wall_share_top_10": round_feature(largest_ask_wall_share_top_10, 4),

    # distance from best level to nearest largest wall
    "largest_bid_wall_distance_from_best_bid_pct": round_feature(largest_bid_wall_distance_from_best_bid_pct, 4),
    "largest_ask_wall_distance_from_best_ask_pct": round_feature(largest_ask_wall_distance_from_best_ask_pct, 4),
}

def save_orderbook_features(bid_orderbook, ask_orderbook, item_name):
    features = build_orderbook_features(bid_orderbook, ask_orderbook, item_name)

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

    save_path = save_dir / "orderbook_features_dataset.json"

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(features_list, f, indent=2)

    logger.info("Saved aggregated orderbook features (%d items) to %s", len(features_list), save_path)

    return save_path