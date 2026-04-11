import logging
import json
import urllib.parse

import config.config as cfg
from src.utils.http import request_json
from src.utils.strings import make_safe_item_name

logger = logging.getLogger(__name__)

def fetch_orderbook(item_name: str, endpoint: str):
    encoded_name = urllib.parse.quote(item_name, safe="")
    url = f"{cfg.API_URL_BASE}/{encoded_name}/{endpoint}"

    logger.debug("%s: fetching orderbook %s", item_name, endpoint)
    data = request_json(
        url,
        params={"start": 0, "count": 100},
        headers={"language": "English", "currency": "USD"},
        )
    
    logger.debug("%s: fetched orderbook %s", item_name, endpoint)
    return data

def save_raw_orderbook(item_name, endpoint: str, data: dict):
    if not data or not isinstance(data, dict):
        raise ValueError(f"{item_name}: invalid orderbook data, refusing to save")
    
    endpoint_dir = cfg.RAW_ORDERBOOK_DIR / f"{endpoint}"
    endpoint_dir.mkdir(parents=True, exist_ok=True)

    save_path = endpoint_dir / f"{item_name.strip()}.json"

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.debug("%s: saved raw orderbook for endpoint: %s to: %s", item_name, endpoint, save_path)

    return save_path

if __name__ == "__main__":
    data = fetch_orderbook("Whiteout Boots", "buyOrders")
    save_raw_orderbook("Whiteout Boots", "buyOrders", data)