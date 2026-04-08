from datetime import datetime, timezone 
from config import ITEM_FEATURES_DIR
import json
from utils import make_safe_item_name

# LAYER 1

def extract_median_prices(normalized_rows):
    prices = [row["median"] for row in normalized_rows]
    return prices

def extract_volumes(normalized_rows):
    volumes = [row["volume"] for row in normalized_rows]
    return volumes

# LAYER 2

def get_row_count(normalized_rows):
    return len(normalized_rows)

def get_first_date(normalized_rows):
    return normalized_rows[0]["date"]

def get_last_date(normalized_rows):
    return normalized_rows[-1]["date"]

def get_latest_price(normalized_rows):
    return normalized_rows[-1]["median"]

def get_latest_volume(normalized_rows):
    return normalized_rows[-1]["volume"]

def get_raw_ath(normalized_prices):
    return max(normalized_prices)

def get_raw_atl(normalized_prices):
    return min(normalized_prices)

def calculate_return_pct(normalized_prices, lookback_days):
    
    if len(normalized_prices) <= lookback_days:
        return None

    current_price = normalized_prices[-1]
    past_price = normalized_prices[-(lookback_days + 1)]

    if past_price == 0:
        return None

    return ((current_price - past_price) / past_price) * 100

def calculate_average_volume(volumes, window):
    if len(volumes) < window:
        return None
    
    return sum(volumes[-window:]) / window

# LAYER 3
    
def round_feature(value, decimals):
    if value is None:
        return None
    
    if isinstance(value, float):
        return round(value, decimals)
    
    return value

def build_item_features(normalized_rows: list, item_name: str):

    row_count = get_row_count(normalized_rows)
    first_date = get_first_date(normalized_rows)
    last_date = get_last_date(normalized_rows)
    latest_price = get_latest_price(normalized_rows)
    latest_volume = get_latest_volume(normalized_rows)

    prices = extract_median_prices(normalized_rows)
    volumes = extract_volumes(normalized_rows)

    raw_ath = get_raw_ath(prices)
    raw_atl = get_raw_atl(prices)

    return_7d = calculate_return_pct(prices, 7)
    return_30d = calculate_return_pct(prices, 30)

    average_volume_7d = calculate_average_volume(volumes, 7)
    average_volume_30d = calculate_average_volume(volumes, 30)

    return {
        "item_name": item_name,
        "row_count": row_count,
        "first_date": first_date,
        "last_date": last_date,
        "latest_price": round_feature(latest_price, 2),
        "latest_volume": latest_volume,
        "raw_ath": round_feature(raw_ath, 2),
        "raw_atl": round_feature(raw_atl, 2),
        "return_7d_pct": round_feature(return_7d, 2),
        "return_30d_pct": round_feature(return_30d, 2),
        "average_volume_7d": round_feature(average_volume_7d, 2),
        "average_volume_30d": round_feature(average_volume_30d, 2),
    }

def save_price_features(features: dict):
    if not isinstance(features, dict):
        raise TypeError("Features must be a dict") 
    if not features:
        raise ValueError("Features cannot be empty")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    save_dir = ITEM_FEATURES_DIR / timestamp
    save_dir.mkdir(parents=True, exist_ok=True)

    item_name = features["item_name"]
    safe_item_name = make_safe_item_name(item_name)
    save_path = save_dir / f"{safe_item_name}-features.json"

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(features, f, indent=2)

    return save_path

def save_price_features_dataset(features_list: list):
    if not isinstance(features_list, list):
        raise TypeError("Features_list must be a list")
    if not features_list:
        raise ValueError("Features_list cannot be empty")
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    save_dir = ITEM_FEATURES_DIR / timestamp
    save_dir.mkdir(parents=True, exist_ok=True)

    save_path = save_dir / f"features_dataset.json"

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(features_list, f, indent=2)

    return save_path