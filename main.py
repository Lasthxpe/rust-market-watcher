import config as cfg
from fetch import fetch_item_data, save_raw_sales
from normalize import normalize_sales_data, save_processed_sales
from validate import validate_raw_item_data
from metrics import get_latest_price, calculate_average_price, calculate_average_volume, calculate_total_volume, get_price_range
from output import build_item_report, build_failed_report, print_item_report, save_reports
import logging
from log_utils import setup_logging

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
    save_processed_sales(item_name, normalized)

    latest_price = get_latest_price(normalized)
    average_price_7d = calculate_average_price(normalized, 7)
    average_price_30d = calculate_average_price(normalized, 30)
    max_price_30d, min_price_30d = get_price_range(normalized, 30)
    average_volume_7d = calculate_average_volume(normalized, 7)
    average_volume_30d = calculate_average_volume(normalized, 30)
    total_volume_30d = calculate_total_volume(normalized, 30)

    return build_item_report(
        item_name,
        latest_price,
        average_price_7d,
        average_price_30d,
        max_price_30d,
        min_price_30d,
        average_volume_7d,
        average_volume_30d,
        total_volume_30d
        )

def main():
    logger.info("Initiating Rust Market Watcher v1.2.2")

    items_path = cfg.BASE_DIR / "items.txt"
    items = load_item_names(items_path)
    logger.info("Loaded %d items from %s", len(items), items_path)

    reports = []
    failed_items  = 0

    for i, item in enumerate(items, start=1):
        logger.info("[%d/%d] Processing %s...", i, len(items), item)
        try:
            report = process_item(item)
        except (ValueError, RuntimeError, OSError) as e:
            logger.warning("Skipping %s: %s", item, e)
            report = build_failed_report(item, str(e))
            failed_items += 1

        print_item_report(report)
        reports.append(report)

    logger.info("Processing complete: %d succeeded, %d failed", (len(reports) - failed_items), failed_items)

    try:
        output_path = save_reports(reports)
    except OSError as e:
        logger.critical("Failed to save final report file: %s", e)
        return

    logger.info("Reports file saved to %s", output_path)

if __name__ == "__main__":
    setup_logging()
    main()