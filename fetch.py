from config import API_URL_BASE
from http_utils import request_json
import logging

logger = logging.getLogger(__name__)

def fetch_item_data(item_name):
    url = f"{API_URL_BASE}/{item_name}/sales"

    data = request_json(
        url,
        params={"maxDays": 31, "ochl": True},
        headers={"language": "English", "currency": "USD"},           
    )
    
    logger.debug("%s: fetching sales data with maxDays=31", item_name)
    return data