def get_latest_price(response):
    return response[-1]["median"]

def calculate_average_price(response, window):
    prices = [entry["median"] for entry in response]
    if len(prices) < window:
        return None
    return sum(prices[-window:]) / window

def calculate_average_volume(response, window):
    volumes = [entry["volume"] for entry in response[:-1]]
    if len(volumes) < window:
        return None
    return sum(volumes[-window:]) / window

def calculate_total_volume(response, window):
    volumes = [entry["volume"] for entry in response[:-1]]
    if len(volumes) < window:
        return None
    return sum(volumes[-window:])

def get_price_range(response, window):
    prices = [entry["median"] for entry in response]

    if len(prices) < window:
        return None, None

    return max(prices[-window:]), min(prices[-window:])    