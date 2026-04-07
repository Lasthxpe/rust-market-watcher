import config as cfg
from datetime import datetime, timezone
import json

def build_item_report(
        item_name, 
        latest_price,
        average_price_7d,
        average_price_30d,
        max_price_30d,
        min_price_30d,
        average_volume_7d,
        average_volume_30d,
        total_volume_30d
):
    return {
        "item_name": item_name,
        "status": "ok",
        "latest_price": latest_price,
        "average_price_7d": average_price_7d,
        "average_price_30d": average_price_30d,
        "max_price_30d": max_price_30d,
        "min_price_30d": min_price_30d,
        "average_volume_7d": average_volume_7d,
        "average_volume_30d": average_volume_30d,
        "total_volume_30d": total_volume_30d,
    }

def build_failed_report(item_name, error):
    return {
        "item_name": item_name,
        "status": "failed",
        "error": error,
    }

def format_metric(value):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.2f}"
    return f"{value}"


def print_item_report(report):
    if report["status"] == "failed":
        print(f"[FAILED] {report['item_name']}")
        print(f"Error: {report['error']}")
        return 
    
    print(f"[OK] {report['item_name']}")
    print(f"   Latest Price: ${format_metric(report['latest_price'])}")
    print(f"   Average Price (7): ${format_metric(report['average_price_7d'])}")
    print(f"   Average Price (30): ${format_metric(report['average_price_30d'])}")
    print(f"   Highest Price (30): ${format_metric(report['max_price_30d'])}")
    print(f"   Lowest Price (30): ${format_metric(report['min_price_30d'])}")
    print(f"   Average Volume (7): {format_metric(report['average_volume_7d'])}")
    print(f"   Average Volume (30): {format_metric(report['average_volume_30d'])}")
    print(f"   Total Volume (30): {format_metric(report['total_volume_30d'])}")
    
def save_reports(reports):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = cfg.DATA_DIR / f"{timestamp}.json"
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="UTF-8") as f:
        json.dump(reports, f, indent=2)

    return report_path