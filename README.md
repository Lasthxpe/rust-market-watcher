# Rust Market Watcher v1.1.0

A Python-based data pipeline for fetching, validating, and analyzing Rust skin market data.

This project focuses on building a solid foundation: clean data ingestion, strict validation, reliable metric computation, and structured output — before moving into advanced analysis.

---

## What is Rust Market Watcher?

Rust Market Watcher is a lightweight market data pipeline built around the SCMM API (https://rust.scmm.app/docs/index.html).

The goal is simple but critical:
> get clean, structured, and reliable market data before doing anything more advanced.

This project acts as the foundation for future systems involving signal detection, ranking, and market intelligence.

---

## Core Features

- Fetches item sales data from the SCMM API
- Validates structure, types, and price consistency
- Computes key price and volume metrics
- Outputs results to console and JSON reports
- Includes structured logging for visibility and debugging

---

## Project Structure

| File | Purpose |
|------|--------|
| `main.py` | Runs the full pipeline |
| `fetch.py` | Fetches item sales data from API |
| `validate.py` | Validates API response structure and values |
| `metrics.py` | Calculates price and volume metrics |
| `output.py` | Builds and prints reports, saves JSON output |
| `http_utils.py` | Handles HTTP requests with retry logic |
| `log_utils.py` | Sets up centralized logging (console + file) |
| `config.py` | Stores paths and configuration settings |
| `items.txt` | Input list of items |
| `data/` | Output directory (reports + logs) |

---

## What It Produces

For each item:

### Price Metrics
- Latest price
- 7-day average
- 30-day average
- 30-day high / low

### Volume Metrics
- 7-day average volume
- 30-day average volume
- 30-day total volume

### Output
- Console summary
- JSON report saved to `/data/YYYY-MM-DD.json`

---

## Logging

The project includes structured logging:

- Console logs for real-time visibility
- File logs stored in `/data/logs/`
- Debug-level logs for fetch and validation steps

This improves traceability and makes debugging significantly easier.

---

## How It Works

1. Load item names from `items.txt`
2. Fetch sales data from the SCMM API
3. Validate the response strictly before use
4. Compute metrics
5. Print results to console
6. Save report to `/data/YYYY-MM-DD.json`

---

## How to Use

Install dependency:

```bash
pip install requests
```

Add items to `items.txt`:

```
Blackout HMLMG
No Mercy Snow Jacket
Heat Seeker SAP
```

Run the pipeline:

```bash
python main.py
```

---

## Example Output

```
[OK] Blackout HMLMG
   Latest Price: $2.37
   Average Price (7): $2.22
   Average Price (30): $2.31
   Highest Price (30): $2.62
   Lowest Price (30): $2.09
   Average Volume (7): 43.14
   Average Volume (30): 43.36
   Total Volume (30): 1301
```

---

## Current Limitations

- Latest-day volume may be partial depending on API response
- Runtime failures (e.g. network issues) are not fully isolated yet
- Some modules do not yet use logging consistently
- No CLI interface yet
- Still a foundation — not a full decision engine

---

## Roadmap

- Stronger runtime error handling
- Full logging integration across all modules
- Additional metrics and signal detection
- CLI-style execution
- Integration into larger market intelligence system

---

## Status

Early-stage, but structured and actively evolving.
