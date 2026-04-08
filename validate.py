from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def validate_raw_date_format(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%dT00:00:00")
        return True
    except ValueError:
        return False

def validate_processed_date_format(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_raw_item_data(response, item_name):
    logger.debug("%s: validating raw item data", item_name)

    if not isinstance(response, list):
        raise TypeError(f"{item_name}: response must be a list.")
    if not response:
        raise ValueError(f"{item_name}: response cannot be empty.")

    required_keys = ["date", "median", "high", "low", "open", "close", "volume"]
    price_keys = ["median", "high", "low", "open", "close"]

    for i, entry in enumerate(response, start=1):
        if not isinstance(entry, dict):
            raise TypeError(f"{item_name}: row {i} must be a dict.")

        for key in required_keys:
            if key not in entry:
                raise ValueError(f"{item_name}: row {i} is missing field: {key}")

        if not isinstance(entry["date"], str):
            raise TypeError(f"{item_name}: row {i} date must be a string")
        if not validate_raw_date_format(entry["date"]):
            raise ValueError(f"{item_name}: row {i} date is of wrong format")

        for key in price_keys:
            if not isinstance(entry[key], (int, float)):
                raise TypeError(f"{item_name}: row {i} field '{key}' must be numeric")
            if entry[key] < 0:
                raise ValueError(f"{item_name}: row {i} field '{key}' cannot be negative")

        if not isinstance(entry["volume"], int):
            raise TypeError(f"{item_name}: row {i} volume must be numeric")

        if entry["volume"] < 0:
            raise ValueError(f"{item_name}: row {i} volume cannot be negative")

        high = entry["high"]
        low = entry["low"]
        open_price = entry["open"]
        close_price = entry["close"]

        if high < max(low, open_price, close_price):
            raise ValueError(f"{item_name}: row {i} has invalid high value")
        if low > min(high, open_price, close_price):
            raise ValueError(f"{item_name}: row {i} has invalid low value")
        
def validate_processed_item_data(normalized_rows, item_name):
    logger.debug("%s: validating processed item data", item_name)

    if not isinstance(normalized_rows, list):
        raise TypeError(f"{item_name}: processed data must be a list")
    if not normalized_rows:
        raise ValueError(f"{item_name}: processed data cannot be empty")
    
    required_keys = ["date", "median", "high", "low", "open", "close", "volume"]
    price_keys = ["median", "high", "low", "open", "close"]
    previous_date = None
    seen_dates = set()

    for i, row in enumerate(normalized_rows, start=1):
        if not isinstance(row, dict):
            raise TypeError(f"{item_name}: row {i} must be a dict")

        for key in required_keys:
            if key not in row:
                raise ValueError(f"{item_name}: row {i} is missing field: {key}")

        if not isinstance(row["date"], str):
            raise TypeError(f"{item_name}: row {i} date must be a string")
        if not validate_processed_date_format(row["date"]):
            raise ValueError(f"{item_name}: row {i} date is of wrong format")
        
        current_date = row["date"]
        
        if current_date in seen_dates:
            raise ValueError(f"{item_name}: row {i} has duplicate date: {current_date}")

        if previous_date is not None and current_date < previous_date:
            raise ValueError(f"{item_name}: row {i} is out of order by date")
        
        previous_date = current_date
        seen_dates.add(current_date)

        for key in price_keys:
            if not isinstance(row[key], float):
                raise TypeError(f"{item_name}: row {i} field '{key}' must be a float")
            if row[key] < 0:
                raise ValueError(f"{item_name}: row {i} field '{key}' cannot be negative")

        if not isinstance(row["volume"], int):
            raise TypeError(f"{item_name}: row {i} volume must be an int")
        if row["volume"] < 0:
            raise ValueError(f"{item_name}: row {i} volume cannot be negative")
        
        high = row["high"]
        low = row["low"]
        open_price = row["open"]
        close_price = row["close"]

        if high < max(low, open_price, close_price):
            raise ValueError(f"{item_name}: row {i} has invalid high value")
        if low > min(high, open_price, close_price):
            raise ValueError(f"{item_name}: row {i} has invalid low value")
    