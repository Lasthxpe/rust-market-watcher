from pathlib import Path

PROJECT_VERSION = "v1.6.0"

# === DIRECTORIES ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# DATA
UNIVERSE_PATH = CONFIG_DIR / "items.txt"
RAW_DATA_DIR = DATA_DIR / "raw"
RAW_SALES_DIR = RAW_DATA_DIR / "sales_history"
RAW_ORDERBOOK_DIR = RAW_DATA_DIR / "orderbook"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PROCESSED_SALES_DIR = PROCESSED_DATA_DIR / "sales_history"
FULL_PRICE_HISTORY_DIR = PROCESSED_DATA_DIR / "full_sales_history"
ITEM_FEATURES_DIR = PROCESSED_DATA_DIR / "features"
REPORTS_DIR = DATA_DIR / "reports"
SCORING_INPUTS_DIR = DATA_DIR / "scoring_inputs"
SCORING_OUTPUTS_DIR = DATA_DIR / "scoring_outputs"
TURNOVER_SCORES_DIR = SCORING_OUTPUTS_DIR / "turnover"
ORDERBOOK_LIQUIDITY_SCORES_DIR = SCORING_OUTPUTS_DIR / "orderbook_liquidity"
POSITION_CONTEXT_DIR = SCORING_OUTPUTS_DIR / "position"
INVESTMENT_CANDIDATES_DIR = DATA_DIR / "scoring_outputs" / "investment_candidates"

# === HTTP / API SETTINGS ===
USER_AGENT = f"HopeMarketWatcher/{PROJECT_VERSION}"
API_URL_BASE = "https://rust.scmm.app/api/item"
REQUEST_TIMEOUT = 15 # Max time to wait for single request - after, abort (secs)
MAX_RETRIES = 3
RETRY_BACKOFF = 2 # Multiplier controlling wait-time between failed HTTP requests (exponential - 1-2-4-8 etc)
STEAM_RATE_LIMIT_SLEEP = 2.0  # Conservative throttle for Steam endpoints
API_RATE_LIMIT_SLEEP = 1 # General throttle for non-Steam APIs
HTTP_VERIFY_SSL = True # Verify HTTPS certificates / security
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

