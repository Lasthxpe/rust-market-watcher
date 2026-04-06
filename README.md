# Rust Market Watcher

A small Python project for fetching, validating, and analyzing Rust skin market data.

This started as a simple foundation for market analysis: pull data, make sure it is valid, calculate useful metrics, and save the results in a consistent format.

---

## What is Rust Market Watcher?

Rust Market Watcher is a lightweight data pipeline built around the SCMM API.

It is meant to solve a basic but important problem first: get clean market data into a structured form before doing anything more advanced with it.

Right now, the project focuses on:

- fetching recent item data
- validating API responses
- calculating simple price and volume metrics
- saving reports in JSON format

The long-term direction is to use this as a base for broader market analysis and signal generation.

---

## What's Inside

Every file has a clear role in the pipeline:

| File | Purpose |
|------|---------|
| `main.py` | Runs the full pipeline |
| `fetch.py` | Fetches item sales data from the API |
| `validate.py` | Validates structure, types, and value consistency |
| `metrics.py` | Calculates price and volume metrics |
| `output.py` | Prints reports and saves JSON output |
| `http_utils.py` | Handles HTTP requests and retry logic |
| `config.py` | Stores paths, API settings, and request config |
| `items.txt` | Input list of items to process |
| `data/` | Output folder for generated reports |

---

## What It Produces

For each item, the project currently calculates:

| Metric Group | Metrics |
|-------------|---------|
| Price | latest price, 7d average, 30d average, 30d high, 30d low |
| Volume | 7d average volume, 30d average volume, 30d total volume |
| Output | console summary + dated JSON report |

---

## How It Works

1. Read item names from `items.txt`
2. Request sales history from the SCMM API
3. Validate the response before using it
4. Calculate metrics from the returned data
5. Print a summary to the console
6. Save the final report to `/data/YYYY-MM-DD.json`

---

## How to Use

1. Install the dependency:

```bash
pip install requests
```

2. Add item names to `items.txt`

```text
Blackout HMLMG
No Mercy Snow Jacket
Heat Seeker SAP
```

3. Run the project:

```bash
python main.py
```

---

## Example Output

```text
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

A JSON report is also saved to:

```text
/data/YYYY-MM-DD.json
```

---

## Current Limitations

- latest-day volume may be partial depending on the API response
- API/runtime failures are not fully isolated yet
- logging is still basic
- this is still a V1 foundation, not a full decision engine

---

## Roadmap

- stronger runtime error handling
- logging instead of print-based reporting
- richer metrics and signal detection
- better CLI-style usage
- integration into a larger market intelligence workflow

---

## Contributing

This is currently a personal project, but the structure is intentionally modular.

Good contribution areas would be:

- improving error handling
- expanding validation rules
- adding new metrics
- improving report formatting
- preparing the project for larger-scale analysis

---

## Status

Early, but functional and actively evolving.
