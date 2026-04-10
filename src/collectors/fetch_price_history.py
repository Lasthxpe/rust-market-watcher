import logging
import json

import config.config as cfg
from src.utils.http import request_json

logger = logging.getLogger(__name__)

def fetch_price_history(item_name, maxDays: int):
    url = f"{cfg.API_URL_BASE}/{item_name}/sales"

    logger.debug("%s: fetching sales data with maxDays=%s", item_name, maxDays)
    data = request_json(
        url,
        params={"maxDays": maxDays, "ochl": True},
        headers={"language": "English", "currency": "USD"},           
    )
    
    logger.debug("%s: fetched sales data successfully", item_name)
    return data

def save_raw_sales(item_name, data):
    if not data or not isinstance(data, list):
        raise ValueError(f"{item_name}: invalid raw data, refusing to save")
    
    save_path = cfg.RAW_SALES_DIR / f"{item_name.strip()}.json"
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.debug("%s: saved raw sales data (%d rows)", item_name, len(data))

    return save_path