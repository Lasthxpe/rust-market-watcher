import logging

import config.config as cfg
from src.collectors.fetch_price_history import fetch_price_history, save_raw_sales
from src.collectors.fetch_orderbook import fetch_orderbook, save_raw_orderbook
from src.processors.normalize_price_history import normalize_sales_data, save_processed_sales
from src.validators.validate_raw_price_history import validate_raw_price_history
from src.validators.validate_processed_price_history import validate_processed_price_history
from src.validators.validate_raw_orderbook import validate_raw_orderbook_data
from src.utils.log_config import setup_logging
from src.processors.price_features import build_item_features, save_price_features, save_price_features_dataset
from src.processors.orderbook_features import build_orderbook_features, save_orderbook_features, save_orderbook_features_dataset


logger = logging.getLogger(__name__)
def load_item_names(path):
    with open(path, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]
    return items

def process_item(item_name: str):
    sales_response = fetch_price_history(item_name, 31)
    validate_raw_price_history(sales_response, item_name)
    raw_sales_path = save_raw_sales(item_name, sales_response)

    sales_normalized = normalize_sales_data(raw_sales_path)
    validate_processed_price_history(sales_normalized, item_name)
    save_processed_sales(item_name, sales_normalized)

    price_features = build_item_features(sales_normalized, item_name)

    buy_orderbook_response = fetch_orderbook(item_name, "buyOrders")
    sell_orderbook_response = fetch_orderbook(item_name, "sellOrders")
    save_raw_orderbook(item_name, "buyOrders", buy_orderbook_response)
    save_raw_orderbook(item_name, "sellOrders", sell_orderbook_response)

    validate_raw_orderbook_data(item_name, "buyOrders", buy_orderbook_response)
    validate_raw_orderbook_data(item_name, "sellOrders", sell_orderbook_response)

    orderbook_features = build_orderbook_features(buy_orderbook_response, sell_orderbook_response, item_name)

    return price_features, orderbook_features

def main():
    logger.info("Initiating Rust Market Watcher v1.4.0")

    items_path = cfg.CONFIG_DIR / "items.txt"
    items = load_item_names(items_path)
    logger.info("Loaded %d items from %s", len(items), items_path)

    price_features_list = []
    orderbook_features_list = []
    failed_items  = 0

    for i, item in enumerate(items, start=1):
        logger.info("[%d/%d] Processing %s...", i, len(items), item)
        try:
            price_features, orderbook_features = process_item(item)
            price_features_list.append(price_features)
            orderbook_features_list.append(orderbook_features)
        except (ValueError, TypeError, RuntimeError, OSError):
            logger.exception("Skipping %s due to processing error", item)
            failed_items += 1

    if price_features_list:
        save_price_features_dataset(price_features_list)
    else:
        logger.warning("No price features dataset saved because all items failed")

    if orderbook_features_list:
        save_orderbook_features_dataset(orderbook_features_list)
    else:
        logger.warning("No orderbook features dataset saved because all items failed")

    logger.info("Processing complete: %d succeeded, %d failed", len(price_features_list), failed_items)
    

if __name__ == "__main__":
    setup_logging()
    main()