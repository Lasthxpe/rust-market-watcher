from config import API_URL_BASE
from http_utils import request_json

def fetch_item_data(item_name):
    url = f"{API_URL_BASE}/{item_name}/sales"

    data = request_json(
        url,
        params={"maxDays": 30, "ochl": True},
        headers={"language": "English", "currency": "USD"},           
    )

    return data