# Rust Market Watcher v1.2.1

A structured data pipeline for collecting, validating, and transforming Rust skin market data into a reliable format for analysis.

This project focuses on building a strong data foundation before introducing higher-level systems such as signal detection, ranking, and automated decision-making.

---

## Overview

Rust Market Watcher is designed as a **data layer for market intelligence**.

Instead of jumping straight into predictions or signals, the project prioritizes:
- clean data ingestion
- strict validation
- consistent normalization
- reproducible outputs

The goal is to ensure that any future system built on top operates on **trustworthy and structured data**.

---

## Current Capabilities

The pipeline currently performs the following steps:

1. Load item names from `items.txt`
2. Fetch raw sales data from the SCMM API
3. Validate raw API response
4. Store raw data per item under `/data/raw/sales_history/`
5. Normalize raw data into a consistent internal format
6. Store processed data under `/data/processed/sales_history/`
7. Compute price and volume metrics
8. Output results to console
9. Save aggregated report to `/data/YYYY-MM-DD.json`

---

## Project Structure

| File | Purpose |
|------|--------|
| `main.py` | Runs the full pipeline |
| `fetch.py` | Handles API data fetching and raw data persistence |
| `validate.py` | Validates raw API response structure and values |
| `normalize.py` | Converts raw data into normalized internal format |
| `metrics.py` | Computes price and volume metrics |
| `output.py` | Handles reporting and output formatting |
| `log_utils.py` | Centralized logging setup (console + file) |
| `config.py` | Stores configuration and directory structure |
| `items.txt` | Input list of tracked items |
| `data/` | Output directory (raw, processed, reports, logs) |

---

## Output

### Per Item
- Latest price
- 7-day and 30-day average price
- 30-day high / low
- 7-day and 30-day average volume
- 30-day total volume

### Generated Files
- Raw data per item → `/data/raw/sales_history/`
- Processed data per item → `/data/processed/sales_history/`
- Daily report → `/data/YYYY-MM-DD.json`
- Logs → `/data/logs/`

---

## Logging

The project includes structured logging:

- Console output for real-time visibility
- File logs stored under `/data/logs/`
- Debug-level logs for fetch, validation, and processing steps

This enables traceability of the full pipeline execution.

---

## Design Principles

- **Data first** — no signals without clean data  
- **Deterministic pipeline** — same input → same output  
- **Separation of concerns** — fetch, validate, normalize, compute, output  
- **Incremental development** — build foundation before complexity  

---

## Current Limitations

- Runtime failures (e.g. network issues) are not fully isolated yet  
- Some modules do not yet use logging consistently  
- File naming is not fully sanitized for edge cases  
- No CLI interface or configuration system yet  
- Pipeline is single-threaded and not optimized for scale  

---

## Direction

This project is intended to evolve into a full market intelligence system.

Planned layers on top of the current pipeline:

- signal detection (dips, recoveries, volume anomalies)  
- item ranking and scoring system  
- historical pattern analysis  
- potential ML-based evaluation models  

The current version focuses strictly on building a **reliable and extensible data foundation** for these systems.

---

## Status

Early-stage, but structured and actively evolving.