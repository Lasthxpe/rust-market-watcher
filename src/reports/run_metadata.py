from datetime import datetime, timezone
import json

import config.config as cfg

PIPELINE_STAGES = [
    "init_logging",
    "load_universe",
    "init_run_metadata",

    "fetch_and_save_raw_sales",
    "normalize_and_save_sales",

    "fetch_and_save_orderbooks",

    "build_features",

    "aggregate_price_features_dataset",
    "aggregate_orderbook_features_dataset",

    "finalize_run_metadata",
    "save_run_metadata"
]

def get_items_count(universe_path):
    with open(universe_path, 'r') as f:
        line_count = 0
        for line in f:
            line_count += 1

    return line_count

def init_run_metadata(items_path):
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    version = cfg.PROJECT_VERSION
    run_date = datetime.today().strftime("%Y-%m-%d")
    start_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    items_count = get_items_count(items_path)

    return {
        "run_id": run_id,
        "version": version,
        "run_date": run_date,
        "start_time": start_time,
        "end_time": None,
        
        "inputs": {
            "items_input_file": str(items_path),
            "items_count": items_count,
        },

        "config_settings": {
            "http_timeout": cfg.REQUEST_TIMEOUT,
            "http_retries": cfg.MAX_RETRIES,
        },

        "pipeline_stages": PIPELINE_STAGES,
    }

def save_run_metadata(run_metadata):
    if not isinstance(run_metadata, dict):
        raise ValueError("Run metadata must be a dict")
    if not run_metadata:
        raise ValueError("Run metadata cannot be empty")

    save_dir = cfg.REPORTS_DIR / run_metadata["run_date"]
    save_dir.mkdir(parents=True, exist_ok=True)

    save_path = save_dir / "run.json"

    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(run_metadata, f, indent=2)

