import config as cfg
from fetch import fetch_item_data, save_raw_sales
from normalize import normalize_sales_data, save_processed_sales
from validate import validate_raw_item_data, validate_processed_item_data
import logging
from log_utils import setup_logging
from price_features import build_item_features, save_price_features, save_price_features_dataset

logger = logging.getLogger(__name__)
def load_item_names(path):
    with open(path, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]
    return items

def process_item(item_name: str) -> dict:
    response = fetch_item_data(item_name, 31)
    validate_raw_item_data(response, item_name)
    raw_sales_path = save_raw_sales(item_name, response)

    normalized = normalize_sales_data(raw_sales_path)
    validate_processed_item_data(normalized, item_name)
    save_processed_sales(item_name, normalized)

    features = build_item_features(normalized, item_name)
    save_price_features(features)

    return features

def main():
    logger.info("Initiating Rust Market Watcher v1.3.0")

    items_path = cfg.BASE_DIR / "items.txt"
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