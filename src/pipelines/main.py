import logging

import config.config as cfg
from src.collectors.fetch_price_history import fetch_price_history, save_raw_sales
from src.processors.normalize_price_history import normalize_sales_data, save_processed_sales
from src.validators.validate_raw_price_history import validate_raw_item_data
from src.validators.validate_processed_price_history import validate_processed_item_data
from src.utils.log_config import setup_logging
from src.processors.price_features import build_item_features, save_price_features, save_price_features_dataset

logger = logging.getLogger(__name__)
def load_item_names(path):
    with open(path, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]
    return items

def process_item(item_name: str) -> dict:
    response = fetch_price_history(item_name, 31)
    validate_raw_item_data(response, item_name)
    raw_sales_path = save_raw_sales(item_name, response)

    normalized = normalize_sales_data(raw_sales_path)
    validate_processed_item_data(normalized, item_name)
    save_processed_sales(item_name, normalized)

    features = build_item_features(normalized, item_name)
    save_price_features(features)

    return features

def main():
    logger.info("Initiating Rust Market Watcher v1.3.1")

    items_path = cfg.CONFIG_DIR / "items.txt"
    items = load_item_names(items_path)
    logger.info("Loaded %d items from %s", len(items), items_path)

    features_list = []
    failed_items  = 0

    for i, item in enumerate(items, start=1):
        logger.info("[%d/%d] Processing %s...", i, len(items), item)
        try:
            features = process_item(item)
            features_list.append(features)
        except (ValueError, RuntimeError, OSError):
            logger.exception("Skipping %s due to processing error", item)
            failed_items += 1

    if features_list:
        save_price_features_dataset(features_list)
    else:
        logger.warning("No features dataset saved because all items failed")

    logger.info("Processing complete: %d succeeded, %d failed", len(features_list), failed_items)
    

if __name__ == "__main__":
    setup_logging()
    main()