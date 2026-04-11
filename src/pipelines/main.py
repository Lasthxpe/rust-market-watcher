import logging
from datetime import datetime, timezone

import config.config as cfg
from src.collectors.fetch_price_history import fetch_price_history, save_raw_sales
from src.collectors.fetch_orderbook import fetch_orderbook, save_raw_orderbook
from src.processors.normalize_price_history import normalize_sales_data, save_processed_sales
from src.validators.validate_raw_price_history import validate_raw_price_history
from src.validators.validate_processed_price_history import validate_processed_price_history
from src.validators.validate_raw_orderbook import validate_raw_orderbook_data
from src.utils.log_config import setup_logging
from src.processors.price_features import build_item_features, save_price_features_dataset
from src.processors.orderbook_features import build_orderbook_features, save_orderbook_features_dataset
from src.reports.run_metadata import init_run_metadata, save_run_metadata


logger = logging.getLogger(__name__)

def load_item_names(path):
    with open(path, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line.strip()]
    return items

def fetch_and_save_raw_sales(item_name: str):

    sales_response = fetch_price_history(item_name, 31)
    validate_raw_price_history(sales_response, item_name)
    raw_sales_path = save_raw_sales(item_name, sales_response)

    return raw_sales_path

def normalize_and_save_sales(item_name, raw_sales_path):

    sales_normalized = normalize_sales_data(raw_sales_path)
    validate_processed_price_history(sales_normalized, item_name)
    save_processed_sales(item_name, sales_normalized)

    return sales_normalized

def fetch_and_save_orderbooks(item_name: str):

    buy_orderbook_response = fetch_orderbook(item_name, "buyOrders")
    sell_orderbook_response = fetch_orderbook(item_name, "sellOrders")

    validate_raw_orderbook_data(item_name, "buyOrders", buy_orderbook_response)
    validate_raw_orderbook_data(item_name, "sellOrders", sell_orderbook_response)

    save_raw_orderbook(item_name, "buyOrders", buy_orderbook_response)
    save_raw_orderbook(item_name, "sellOrders", sell_orderbook_response)

    return buy_orderbook_response, sell_orderbook_response

def build_features(item_name: str, sales_normalized, buy_orderbook_response, sell_orderbook_response):

    price_features = build_item_features(sales_normalized, item_name)
    orderbook_features = build_orderbook_features(buy_orderbook_response, sell_orderbook_response, item_name)

    return price_features, orderbook_features


def main():
    logger.info("Initiating Rust Market Watcher %s", cfg.PROJECT_VERSION)


    items_path = cfg.UNIVERSE_PATH
    items = load_item_names(items_path)
    logger.info("Loaded %d items from %s", len(items), items_path)

    run_metadata = init_run_metadata(items_path)

    price_features_list = []
    orderbook_features_list = []
    failed_items = 0
    successful_items = 0

    for i, item in enumerate(items, start=1):
        logger.info("[%d/%d] Processing %s...", i, len(items), item)
        try:
            raw_sales_path = fetch_and_save_raw_sales(item)
            sales_normalized = normalize_and_save_sales(item, raw_sales_path)
            buy_orderbook_response, sell_orderbook_response = fetch_and_save_orderbooks(item)

            price_features, orderbook_features = build_features(
                item, 
                sales_normalized, 
                buy_orderbook_response, 
                sell_orderbook_response
            )

            price_features_list.append(price_features)
            orderbook_features_list.append(orderbook_features)
            successful_items += 1
        except (ValueError, TypeError, RuntimeError, OSError):
            logger.exception("Skipping %s due to processing error", item)
            failed_items += 1

    if len(price_features_list) != len(orderbook_features_list):
        raise RuntimeError("Mismatch between price and orderbook features count")

    if price_features_list:
        save_price_features_dataset(price_features_list)
    else:
        logger.warning("No price features dataset saved because all items failed")

    if orderbook_features_list:
        save_orderbook_features_dataset(orderbook_features_list)
    else:
        logger.warning("No orderbook features dataset saved because all items failed")

    metadata_end_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_metadata["end_time"] = metadata_end_time
    save_run_metadata(run_metadata)

    logger.info("Pipeline complete: %d succeeded, %d failed", successful_items, failed_items)
    

if __name__ == "__main__":
    setup_logging()
    main()