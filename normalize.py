import json
import logging
from config import PROCESSED_SALES_DIR, RAW_SALES_DIR

logger = logging.getLogger(__name__)

def normalize_sales_data(raw_path):
    if not raw_path.is_file():
        raise ValueError(f"JSON file not found at: {raw_path}")
    with open(raw_path, 'r', encoding="utf-8") as f:
        data = json.load(f)

    normalized_rows = []

    for i, entry in enumerate(data):

        if not isinstance(entry, dict):
            raise ValueError(f"Entry #{i} is not a dict")
        
        try:
            row = {
                "date": entry["date"][:10],
                "median": float(entry["median"]),
                "open": float(entry["open"]),
                "close": float(entry["close"]),
                "high": float(entry["high"]),
                "low": float(entry["low"]),
                "volume": int(entry["volume"]),
            }
        except Exception as e:
            logger.warning("%s: failed to create normalized row for at entry #%d: %s", raw_path.name, i, e)
            continue
        
        normalized_rows.append(row)

    if not normalized_rows:
            raise ValueError(f"{raw_path.name}: 0 valid rows out of {len(data)} entries")
        
    normalized_rows = sorted(normalized_rows, key=lambda row: row["date"])

    return normalized_rows
    
def save_processed_sales(item_name, normalized_rows):
    if not normalized_rows or not isinstance(normalized_rows, list):
        raise ValueError(f"{item_name}: invalid processed data, refusing to save")
    
    save_path = PROCESSED_SALES_DIR / f"{item_name.strip()}.json"
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(normalized_rows, f, indent=2, ensure_ascii=False)

    logger.debug("%s: saved processed sales data (%d rows)", item_name, len(normalized_rows))

    return save_path
