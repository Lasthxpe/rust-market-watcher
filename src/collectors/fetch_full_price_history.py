import json
import logging
from datetime import datetime
from pathlib import Path

import config.config as cfg
from src.collectors.fetch_price_history import fetch_price_history

logger = logging.getLogger(__name__)


def parse_row_date(row: dict) -> datetime:
    return datetime.fromisoformat(row["date"])


def load_existing_history(path: Path) -> list[dict]:
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Existing full price history is not a list: {path}")

    return data


def get_latest_saved_date(rows: list[dict]) -> datetime | None:
    if not rows:
        return None

    latest_row = max(rows, key=parse_row_date)
    return parse_row_date(latest_row)


def merge_price_history(existing_rows: list[dict], fresh_rows: list[dict]) -> list[dict]:
    merged = {}

    for row in existing_rows:
        if not isinstance(row, dict):
            raise ValueError("Existing price history row is not a dict")
        if "date" not in row:
            raise ValueError("Existing price history row missing 'date'")

        merged[row["date"]] = row

    for row in fresh_rows:
        if not isinstance(row, dict):
            raise ValueError("Fresh price history row is not a dict")
        if "date" not in row:
            raise ValueError("Fresh price history row missing 'date'")

        merged[row["date"]] = row

    merged_rows = list(merged.values())
    merged_rows.sort(key=parse_row_date)

    return merged_rows


def save_full_price_history(item_name: str, rows: list[dict]) -> Path:
    if not rows:
        raise ValueError(f"{item_name}: refusing to save empty full price history")

    cfg.FULL_PRICE_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    save_path = cfg.FULL_PRICE_HISTORY_DIR / f"{item_name.strip()}.json"

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    logger.info("%s: saved full price history (%d rows)", item_name, len(rows))

    return save_path


def fetch_full_price_history(item_name: str) -> Path:
    cfg.FULL_PRICE_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    save_path = cfg.FULL_PRICE_HISTORY_DIR / f"{item_name.strip()}.json"

    existing_rows = load_existing_history(save_path)
    latest_saved_date = get_latest_saved_date(existing_rows)

    if latest_saved_date is None:
        max_days = -1
        logger.info("%s: no full history found, fetching full history", item_name)
    else:
        today = datetime.today().date()
        days_since_latest = (today - latest_saved_date.date()).days
        max_days = max(7, days_since_latest + 3)

        logger.info(
            "%s: updating full history from %s, fetching last %d days",
            item_name,
            latest_saved_date.date().isoformat(),
            max_days,
        )

    fresh_rows = fetch_price_history(item_name, maxDays=max_days)

    if not fresh_rows or not isinstance(fresh_rows, list):
        raise ValueError(f"{item_name}: invalid fresh full price history data")

    final_rows = merge_price_history(existing_rows, fresh_rows)

    return save_full_price_history(item_name, final_rows)


def fetch_full_price_histories(item_names: list[str]) -> list[Path]:
    logger.info("Starting full price history fetch for %d items", len(item_names))

    saved_paths = []
    success_count = 0
    failure_count = 0

    for index, item_name in enumerate(item_names, start=1):
        item_name = item_name.strip()

        try:
            logger.info("[%d/%d] Fetching full price history for %s", index, len(item_names), item_name)

            save_path = fetch_full_price_history(item_name)

            saved_paths.append(save_path)
            success_count += 1

        except Exception:
            failure_count += 1
            logger.exception("Failed to fetch full price history for item: %s", item_name)

    logger.info(
        "Finished full price history fetch: %d succeeded, %d failed, %d total",
        success_count,
        failure_count,
        len(item_names),
    )

    return saved_paths