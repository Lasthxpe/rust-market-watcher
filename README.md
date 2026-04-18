# Rust Market Watcher v1.5.0

A structured data pipeline for collecting, validating, and transforming
Rust skin market data into machine-usable feature datasets, scoring inputs,
and deterministic signal outputs for analysis.

This project focuses on building a strong data foundation and layering
interpretable scoring systems on top of it, starting with deterministic
signals such as liquidity evaluation.

------------------------------------------------------------------------

## Overview

Rust Market Watcher is designed as a **data layer for market
intelligence**.

Instead of jumping straight into predictions or signals, the project
prioritizes: 
-   clean data ingestion 
-   multi-layer validation (raw + processed) 
-   enforced types, ordering, and data integrity 
-   consistent normalization 
-   safe item-name handling for file saves
-   reproducible outputs

The goal is to ensure that any future system built on top operates on
**trustworthy and structured data**.

------------------------------------------------------------------------

## Current Capabilities

The pipeline currently performs the following steps:

1. Load item names from `config/items.txt`
2. Fetch raw sales data from the SCMM API
3. Validate raw sales data
4. Store raw sales data per item under `/data/raw/sales_history/`
5. Normalize raw sales data into a consistent internal format
6. Validate processed (normalized) data
7. Store processed sales data under `/data/processed/sales_history/`
8. Compute deterministic price features (returns, liquidity, etc.)
9. Fetch raw orderbook data (buyOrders & sellOrders)
10. Validate raw orderbook data
11. Store raw orderbook data under `/data/raw/orderbook/`
12. Compute orderbook features (spread, depth, imbalance, walls)
13. Save aggregated datasets for price and orderbook features
14. Build merged scoring input rows from price and orderbook features
15. Save scoring input dataset
16. Compute deterministic liquidity scores
17. Save liquidity score dataset
18. Generate run metadata report
------------------------------------------------------------------------

## Project Structure

| Path | Purpose |
|------|--------|
| `src/pipelines/main.py` | Runs the full pipeline |
| `src/collectors/fetch_price_history.py` | Handles API data fetching and raw data persistence |
| `src/collectors/fetch_orderbook.py` | Fetches and saves raw orderbook data |
| `src/processors/normalize_price_history.py` | Converts raw data into normalized internal format |
| `src/processors/price_features.py` | Builds deterministic per-item feature sets and handles feature persistence |
| `src/processors/orderbook_features.py` | Builds orderbook-based features |
| `src/processors/ranking_inputs.py` | Builds merged scoring-input rows from price and orderbook features |
| `src/validators/validate_raw_price_history.py` | Validates raw API data |
| `src/validators/validate_processed_price_history.py` | Validates processed (normalized) data |
| `src/validators/validate_raw_orderbook.py` | Validates raw orderbook structure |
| `src/signals/liquidity.py` | Computes deterministic liquidity scores and handles score persistence |
| `src/utils/math.py` | Shared math utilities (rounding, etc.) |
| `src/utils/log_config.py` | Centralized logging setup (console + file) |
| `src/utils/http.py` | HTTP client with retries, backoff, and JSON parsing |
| `src/utils/strings.py` | String helpers (safe filenames, etc.) |
| `src/reports/run_metadata.py` | Generates run-level metadata (timing, inputs, summary) |
| `config/config.py` | Stores configuration and directory structure |
| `config/items.txt` | Input list of tracked items |
| `data/` | Output directory (raw, processed, logs) |
  -----------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## Features & Output

### Price Features

-   First and last available date
-   Latest price
-   Latest volume
-   Latest complete volume (most recent reliable datapoint)
-   Raw all-time high and low
-   7-day and 30-day returns
-   7-day and 30-day average volume

### Orderbook Features

-   Best bid / best ask price and quantity
-   Spread (absolute and percentage)
-   Top-N depth (bid and ask)
-   Depth imbalance
-   Gap to second ask level
-   Largest bid/ask wall within top N levels

### Scoring Inputs

-   Merged per-item dataset combining price and orderbook features
-   Flat structure designed for downstream scoring and ranking

### Liquidity Signal

-   Liquidity gate based on 30-day average volume
-   Strength classification based on 30-day volume tiers
-   Trend evaluation using 7-day vs 30-day volume ratio
-   Final bounded liquidity score (0–20)
-   Output includes label, flags, reasons, and trace fields

### Generated Files

-   Raw data per item → `/data/raw/sales_history/`
-   Raw orderbook data → `/data/raw/orderbook/`
-   Processed data per item → `/data/processed/sales_history/`
-   Price feature dataset → `/data/processed/features/YYYY-MM-DD/price_features_dataset.json`
-   Orderbook feature dataset → `/data/processed/features/YYYY-MM-DD/orderbook_features_dataset.json`
-   Scoring input dataset → `/data/processed/scoring_inputs/YYYY-MM-DD.json`
-   Liquidity score dataset → `/data/processed/liquidity_scores/YYYY-MM-DD.json`
-   Run metadata report → `/data/reports/YYYY-MM-DD/run_metadata.json`
-   Logs → `/data/logs/`

------------------------------------------------------------------------

## Logging

The project includes structured logging:

-   Console output for real-time visibility
-   File logs stored under `/data/logs/`
-   Debug-level logs for fetch, validation, processing, and feature
    computation steps

This enables traceability of the full pipeline execution.

------------------------------------------------------------------------

## Design Principles

-   **Data first** --- signals are built only on validated and structured data
-   **Deterministic pipeline** --- same input → same output\
-   **Separation of concerns** --- collectors, validators, processors,
    pipelines, utils\
-   **Incremental development** --- build foundation before complexity

------------------------------------------------------------------------

## Current Limitations

-   Runtime failures (e.g. network issues) are not fully isolated yet\
-   Pipeline is single-threaded and not optimized for scale\
-   No CLI interface or configuration system yet
-   Only liquidity scoring signal is implemented so far (no composite multi-signal ranking system yet)
-   Scoring thresholds and weights are still subject to tuning

------------------------------------------------------------------------

## Direction

The project is now transitioning from a pure data pipeline into a full market intelligence system, starting with deterministic scoring signals.

Planned layers on top of the current pipeline:

-   additional deterministic signals (spread, depth, entry position, etc.)
-   composite item ranking system across multiple signals
-   historical pattern analysis
-   potential ML-based evaluation models

The current version establishes a reliable data foundation and introduces
the first deterministic scoring layer, beginning the transition toward a
full market intelligence system.

------------------------------------------------------------------------

## Status

Early-stage, structured, and actively evolving.

