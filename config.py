from pathlib import Path

# === DIRECTORIES ===
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"

# DATA
RAW_DATA_DIR = DATA_DIR / "raw"
RAW_SALES_DIR = RAW_DATA_DIR / "sales_history"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PROCESSED_SALES_DIR = PROCESSED_DATA_DIR / "sales_history"
ITEM_FEATURES_DIR = PROCESSED_DATA_DIR / "features"

# === HTTP / API SETTINGS ===
USER_AGENT = "HopeMarketWatcher/1.3"
API_URL_BASE = "https://rust.scmm.app/api/item"
REQUEST_TIMEOUT = 15 # Max time to wait for single request - after, abort (secs)
MAX_RETRIES = 3
RETRY_BACKOFF = 2 # Multiplier controlling wait-time between failed HTTP requests (exponential - 1-2-4-8 etc)
STEAM_RATE_LIMIT_SLEEP = 2.0  # Conservative throttle for Steam endpoints
API_RATE_LIMIT_SLEEP = 1 # General throttle for non-Steam APIs
HTTP_VERIFY_SSL = True # Verify HTTPS certificates / security
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

