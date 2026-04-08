# Rust Market Watcher v1.3.1

A structured data pipeline for collecting, validating, and transforming
Rust skin market data into machine-usable feature datasets for analysis.
The system produces per-item features and aggregated datasets that can
be used for analysis, ranking, and future decision-making systems.

This project focuses on building a strong data foundation before
introducing higher-level systems such as signal detection, ranking, and
automated decision-making.

------------------------------------------------------------------------

## Overview

Rust Market Watcher is designed as a **data layer for market
intelligence**.

Instead of jumping straight into predictions or signals, the project
prioritizes: - clean data ingestion - multi-layer validation (raw +
processed) - enforced types, ordering, and data integrity - consistent
normalization - reproducible outputs

The goal is to ensure that any future system built on top operates on
**trustworthy and structured data**.

------------------------------------------------------------------------

## Current Capabilities

The pipeline currently performs the following steps:

1.  Load item names from `config/items.txt`
2.  Fetch raw sales data from the SCMM API
3.  Validate raw API response
4.  Store raw data per item under `/data/raw/sales_history/`
5.  Normalize raw data into a consistent internal format
6.  Validate processed (normalized) data
7.  Store processed data under `/data/processed/sales_history/`
8.  Compute deterministic per-item features (price, returns, liquidity)
9.  Save per-item feature files under
    `/data/processed/features/YYYY-MM-DD/`
10. Save aggregated feature dataset for the run

------------------------------------------------------------------------

## Project Structure

| Path | Purpose |
|------|--------|
| `src/pipelines/main.py` | Runs the full pipeline |
| `src/collectors/fetch_price_history.py` | Handles API data fetching and raw data persistence |
| `src/validators/validate_raw_price_history.py` | Validates raw API data |
| `src/validators/validate_processed_price_history.py` | Validates processed (normalized) data |
| `src/processors/normalize_price_history.py` | Converts raw data into normalized internal format |
| `src/processors/price_features.py` | Builds deterministic per-item feature sets and handles feature persistence |
| `src/utils/log_config.py` | Centralized logging setup (console + file) |
| `config/config.py` | Stores configuration and directory structure |
| `config/items.txt` | Input list of tracked items |
| `data/` | Output directory (raw, processed, logs) |
  -----------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## Features & Output

### Per Item

-   Row count
-   First and last available date
-   Latest price
-   Latest volume
-   Raw all-time high and low
-   7-day and 30-day returns
-   7-day and 30-day average volume

### Generated Files

-   Raw data per item → `/data/raw/sales_history/`
-   Processed data per item → `/data/processed/sales_history/`
-   Per-item feature files → `/data/processed/features/YYYY-MM-DD/`
-   Aggregated feature dataset →
    `/data/processed/features/YYYY-MM-DD/features_dataset.json`
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

-   **Data first** --- no signals without clean data\
-   **Deterministic pipeline** --- same input → same output\
-   **Separation of concerns** --- collectors, validators, processors,
    pipelines, utils\
-   **Incremental development** --- build foundation before complexity

------------------------------------------------------------------------

## Current Limitations

-   Runtime failures (e.g. network issues) are not fully isolated yet\
-   Pipeline is single-threaded and not optimized for scale\
-   No CLI interface or configuration system yet

------------------------------------------------------------------------

## Direction

This project is intended to evolve into a full market intelligence
system.

Planned layers on top of the current pipeline:

-   signal detection (dips, recoveries, volume anomalies)\
-   item ranking and scoring system\
-   historical pattern analysis\
-   potential ML-based evaluation models

The current version focuses strictly on building a **reliable and
extensible data foundation** for these systems.

------------------------------------------------------------------------

## Status

Early-stage, structured, and actively evolving.
