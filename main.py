import config as cfg
from fetch import fetch_item_data
from validate import validate_item_data
from metrics import get_latest_price, calculate_average_price, calculate_average_volume, calculate_total_volume, get_price_range
from output import build_item_report, build_failed_report, print_item_report, save_reports

def load_item_names(path):
    with open(path, "r", encoding="utf-8") as f:
        items = [line.strip() for line in f if line]
    return items

def main():
    items = load_item_names(cfg.BASE_DIR / "items.txt")
    reports = []

    for item in items:
        try:
            response = fetch_item_data(item)
            validate_item_data(response, item)

            latest_price = get_latest_price(response)
            average_price_7d = (calculate_average_price(response, 7))
            average_price_30d = calculate_average_price(response, 30)
            max_price_30d, min_price_30d = get_price_range(response, 30)
            average_volume_7d = calculate_average_volume(response, 7)
            average_volume_30d = calculate_average_volume(response, 30)
            total_volume_30d = calculate_total_volume(response, 30)

            report = build_item_report(
                item,
                latest_price,
                average_price_7d,
                average_price_30d,
                max_price_30d,
                min_price_30d,
                average_volume_7d,
                average_volume_30d,
                total_volume_30d
            )

            print_item_report(report)
            reports.append(report)

        except ValueError as e:
            report = build_failed_report(item, str(e))
            print_item_report(report)
            reports.append(report)

    save_reports(reports)

if __name__ == "__main__":
    main()