# Rust Market Watcher v1.6.0

A structured data pipeline for collecting, validating, and transforming
Rust skin market data into machine-usable feature datasets, scoring inputs,
and deterministic signal outputs for analysis.

This project focuses on building a strong data foundation and layering
interpretable scoring systems on top of it, starting with deterministic
signals such as turnover-based liquidity evaluation.

------------------------------------------------------------------------

## Overview

Rust Market Watcher is designed as a **data layer for market intelligence**.

Instead of jumping straight into predictions or signals, the project
prioritizes:

- clean data ingestion  
- multi-layer validation (raw + processed)  
- enforced types, ordering, and data integrity  
- consistent normalization  
- safe item-name handling for file saves  
- reproducible outputs  

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
9. Fetch raw orderbook data (bid/ask)
10. Validate raw orderbook data
11. Store raw orderbook data under `/data/raw/orderbook/`
12. Compute orderbook features (spread, depth, imbalance, walls)
13. Save aggregated datasets for price and orderbook features
14. Build merged scoring input rows from price and orderbook features
15. Save scoring input dataset
16. Compute deterministic turnover scores
17. Compute deterministic orderbook liquidity scores
18. Build full price history dataset (incremental)
19. Evaluate position context signal
20. Build investment candidate dataset
21. Generate run metadata report

------------------------------------------------------------------------

## Project Structure

| Path | Purpose |
|------|--------|
| `src/pipelines/main.py` | Runs the full pipeline |
| `src/pipelines/investment_candidates.py` | Builds investment candidate outputs |
| `src/collectors/fetch_price_history.py` | Handles API data fetching and raw data persistence |
| `src/collectors/fetch_orderbook.py` | Fetches and saves raw orderbook data |
| `src/collectors/fetch_full_price_history.py` | Maintains full incremental price history |
| `src/processors/normalize_price_history.py` | Converts raw data into normalized internal format |
| `src/processors/price_features.py` | Builds deterministic per-item feature sets |
| `src/processors/orderbook_features.py` | Builds orderbook-based features |
| `src/processors/ranking_inputs.py` | Builds merged scoring-input rows |
| `src/validators/validate_raw_price_history.py` | Validates raw API data |
| `src/validators/validate_processed_price_history.py` | Validates processed data |
| `src/validators/validate_raw_orderbook.py` | Validates raw orderbook structure |
| `src/signals/turnover.py` | Computes turnover-based scores |
| `src/signals/orderbook_liquidity.py` | Computes orderbook liquidity scores |
| `src/signals/position.py` | Computes position context signals |
| `src/utils/math.py` | Shared math utilities |
| `src/utils/log_config.py` | Centralized logging |
| `src/utils/http.py` | HTTP client |
| `src/utils/strings.py` | String helpers |
| `src/reports/run_metadata.py` | Run metadata |
| `config/config.py` | Configuration |
| `config/items.txt` | Input universe |
| `data/` | Output directory |

------------------------------------------------------------------------

## Features & Output

### Price Features

- First and last available date  
- Latest price  
- Latest volume  
- Latest complete volume  
- Raw all-time high and low  
- 7-day and 30-day returns  
- 7-day and 30-day average volume  

### Orderbook Features

- Best bid / best ask price and size  
- Spread (absolute and percentage)  
- Top-N depth (bid and ask, top-5 and top-10)  
- Depth imbalance (top-5 and top-10)  
- Gap to second level (bid and ask)  
- Largest bid/ask wall within top N levels  
- Wall share relative to total visible depth  
- Best-level concentration (share of depth at touch)  
- Best-level imbalance (normalized bid vs ask pressure)  
- Distance from best level to largest wall  

### Scoring Inputs

- Merged per-item dataset combining price and orderbook features  
- Flat structure for downstream scoring  

### Turnover Signal

- Turnover gate based on 30-day average volume  
- Strength classification based on volume tiers  
- Trend via 7-day vs 30-day ratio  
- Final bounded score (0–20)  

### Orderbook Liquidity Signal

- Orderbook structure scoring  
- Spread quality evaluation  
- Depth strength evaluation  
- Bid/ask imbalance analysis  
- Final bounded liquidity score  

### Position Context Signal

- Structural ATH/ATL analysis  
- Absolute and structural position ranges  
- State classification  
- Market condition flags  
- Primary bias assignment  

### Investment Candidate Pipeline

- Combined market score (turnover + liquidity)
- Position-based filtering
- Action grouping
- Setup type classification
- Candidate prioritization

### Generated Files

- Raw sales → `/data/raw/sales_history/`  
- Raw orderbook → `/data/raw/orderbook/`  
- Processed sales → `/data/processed/sales_history/`  
- Full price history → `/data/processed/full_sales_history/`
- Price features → `/data/processed/features/YYYY-MM-DD/price_features_dataset.json`  
- Orderbook features → `/data/processed/features/YYYY-MM-DD/orderbook_features_dataset.json`  
- Scoring inputs → `/data/processed/scoring_inputs/YYYY-MM-DD.json`  
- Turnover scores → `/data/scoring_outputs/turnover/YYYY-MM-DD.json`  
- Orderbook liquidity scores → `/data/scoring_outputs/orderbook_liquidity/`
- Position context → `/data/scoring_outputs/position/`
- Investment candidates → `/data/scoring_outputs/investment_candidates/`
- Run metadata → `/data/reports/YYYY-MM-DD/run_metadata.json`  
- Logs → `/data/logs/`  

------------------------------------------------------------------------

## Logging

- Console output  
- File logs (`/data/logs/`)  
- Debug-level tracing across pipeline  

------------------------------------------------------------------------

## Design Principles

- **Data first**
- **Deterministic pipeline**
- **Separation of concerns**
- **Incremental development**

------------------------------------------------------------------------

## Current Limitations

- Runtime failures not fully isolated  
- Single-threaded execution  
- No CLI/config system  
- Signal stack still incomplete
- Investment logic still being refined
- No live portfolio tracking yet
- Scoring still being refined  

------------------------------------------------------------------------

## Direction

The project is transitioning into a full market intelligence system,
currently operating on turnover, orderbook liquidity, and position context,
with investment candidate generation now integrated.

Planned:

- additional deterministic signals  
- multi-signal ranking system  
- historical pattern analysis  
- ML-based evaluation  

------------------------------------------------------------------------

## Status

Early-stage, structured, actively evolving.