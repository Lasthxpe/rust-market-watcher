import json
import logging
from datetime import datetime

import config.config as cfg

logger = logging.getLogger(__name__)

def index_feature_rows_by_item_name(feature_rows):
    indexed_rows = {}

    if not isinstance(feature_rows, list):
        raise TypeError("feature_rows must be a list")

    for row in feature_rows:
        if not isinstance(row, dict):
            raise TypeError("row must be a dict")

        item_name = row.get("item_name")

        if not isinstance(item_name, str):
            raise TypeError(f"{item_name}: item_name must be a string")
        
        if not item_name:
            raise ValueError("Invalid item_name")
        
        if item_name in indexed_rows:
            raise ValueError(f"{item_name}: Duplicate item_name")

        indexed_rows[item_name] = row

    return indexed_rows

def build_all_items_list(price_features_index: dict, orderbook_features_index: dict) -> list:
    all_item_names = []

    for key in price_features_index:
        all_item_names.append(key)

    for key in orderbook_features_index:
        all_item_names.append(key)

    all_item_names = sorted(set(all_item_names))

    return all_item_names

def build_scoring_input_rows(price_features_list, orderbook_features_list):

    indexed_price_features = index_feature_rows_by_item_name(price_features_list)
    indexed_orderbook_features = index_feature_rows_by_item_name(orderbook_features_list)

    all_item_names = build_all_items_list(indexed_price_features, indexed_orderbook_features)

    scoring_input_rows = []

    for item_name in all_item_names:
        price_row = indexed_price_features.get(item_name)
        orderbook_row = indexed_orderbook_features.get(item_name)

        scoring_row = {}

        scoring_row["item_name"] = item_name
        scoring_row["has_price_features"] = price_row is not None
        scoring_row["has_orderbook_features"] = orderbook_row is not None

        if price_row is not None:
            for key, value in price_row.items():
                if key != "item_name":
                    scoring_row[key] = value

        if orderbook_row is not None:
            for key, value in orderbook_row.items():
                if key != "item_name":
                    scoring_row[key] = value

        scoring_input_rows.append(scoring_row)

    return scoring_input_rows

def save_scoring_input_rows(scoring_input_rows):
    timestamp = datetime.today().strftime("%Y-%m-%d")

    cfg.SCORING_INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    save_path = cfg.SCORING_INPUTS_DIR / f"{timestamp}.json"

    with open(save_path, 'w', encoding="UTF-8") as f:
        json.dump(scoring_input_rows, f, indent=2)

    logger.info("Created scoring inputs at %s", save_path)

    return save_path