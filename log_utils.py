import config as cfg
from datetime import datetime, timezone
import logging

def setup_logging(level=logging.INFO):

    # create logs folder
    logs_dir = cfg.LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-T%H%M%SZ")
    log_file = logs_dir / f"{timestamp}.log"

    # format fo logs
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # clear old handers
    logger.handlers.clear()

    # console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # file output
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)