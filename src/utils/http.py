import requests, json, time
from typing import Any

import config.config as cfg

def request_text(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float | None = None,
    ) -> str:

    if headers is None:
        headers = {}
    else:
        headers = dict(headers)

    headers.setdefault("User-Agent", cfg.USER_AGENT)
    

    effective_timeout = cfg.REQUEST_TIMEOUT if timeout is None else timeout
    if effective_timeout <= 0:
        raise ValueError("Timeout must be > 0")
    
    for attempt in range(cfg.MAX_RETRIES + 1): 
        try:
            resp = requests.get(
            url, 
            params=params,
            headers=headers,
            timeout=effective_timeout,
            verify=cfg.HTTP_VERIFY_SSL,
            )
            if resp.status_code in cfg.RETRYABLE_STATUS_CODES and attempt < cfg.MAX_RETRIES:
                sleep_seconds = cfg.RETRY_BACKOFF ** attempt
                time.sleep(sleep_seconds)
                continue
            
            resp.raise_for_status()
            return resp.text

        except requests.RequestException as e:
            if attempt < cfg.MAX_RETRIES:
                sleep_seconds = cfg.RETRY_BACKOFF ** attempt
                time.sleep(sleep_seconds)
                continue
            else:
                raise RuntimeError(f"HTTP request failed after {cfg.MAX_RETRIES + 1} attempts: url={url}, params={params}") from e

def request_json(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float | None = None,
    ) -> Any:

    text = request_text(
        url, 
        params=params, 
        headers=headers, 
        timeout=timeout,
    )
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Response is not a valid JSON: {url}") from e
    
    return data