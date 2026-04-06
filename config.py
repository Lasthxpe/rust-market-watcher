from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

API_URL_BASE = "https://rust.scmm.app/api/item/"

# === HTTP / API SETTINGS ===
USER_AGENT = "HopeMarketWatcher/1.0"
REQUEST_TIMEOUT = 15 # Max time to wait for single request - after, abort (secs)
MAX_RETRIES = 3
RETRY_BACKOFF = 2 # Multiplier controlling wait-time between failed HTTP requests (exponential - 1-2-4-8 etc)
STEAM_RATE_LIMIT_SLEEP = 2.0  # Conservative throttle for Steam endpoints
API_RATE_LIMIT_SLEEP = 1    # General throttle for non-Steam APIs
HTTP_VERIFY_SSL = True # Verify HTTPS certificates / security
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

