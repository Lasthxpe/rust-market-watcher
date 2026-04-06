from datetime import datetime

def validate_date_format(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%dT00:00:00")
        return True
    except ValueError:
        return False

def validate_item_data(response, item_name):
    if not isinstance(response, list):
        raise ValueError(f"{item_name}: expected response to be a list.")
    if not response:
        raise ValueError(f"{item_name}: response cannot be empty.")
    
    required_keys = ["date", "median", "high", "low", "open", "close", "volume"]
    price_keys = ["median", "high", "low", "open", "close"]

    for i, entry in enumerate(response, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"{item_name}: row {i} must be a dict.")

        for key in required_keys:
            if key not in entry:
                raise ValueError(f"{item_name}: row {i} is missing key: {key}")
            
        if not isinstance(entry["date"], str):
            raise ValueError(f"{item_name}: row {i} date must be a string")
        if not validate_date_format(entry["date"]):
            raise ValueError(f"{item_name}: row {i} date is of wrong format")

        for key in price_keys:
            if not isinstance(entry[key], (int, float)):
                raise ValueError(f"{item_name}: row {i} key '{key}' must be numeric")
        
        if not isinstance(entry["volume"], int):
            raise ValueError(f"{item_name}: row {i} volume must be numeric")
        
        for key in price_keys:
            if entry[key] < 0:
                raise ValueError(f"{item_name}: row {i} key '{key}' cannot be negative")
        
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

