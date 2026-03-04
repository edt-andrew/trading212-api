# Examples

The `examples/` folder contains small Python scripts that demonstrate the **trading212-api** client by calling Trading 212 API endpoints and saving the JSON response to a file.

## What they are

Each example is a single script that:

1. Reads your API credentials from the environment (`TRADING212_API_KEY`, `TRADING212_API_SECRET`).
2. Creates a `Trading212Client` against the **demo** (paper) environment.
3. Calls one or more API methods (account, instruments, orders, positions, or historical events).
4. Writes the response as JSON to a file in `examples/`, e.g. `example-account-response.json`.

They are intended to show how to use the client and what the API returns, and to keep sample response JSON in the repo for reference.

## Scripts and outputs

| Script | What it does | Output file |
|--------|--------------|-------------|
| `example-account.py` | Fetches account summary (cash, investments, total value). | `example-account-response.json` |
| `example-instrument.py` | Fetches exchanges metadata and all tradable instruments. | `example-instrument-response.json` |
| `example-orders.py` | Fetches all pending (active) orders. | `example-orders-response.json` |
| `example-positions.py` | Fetches all open positions. | `example-positions-response.json` |
| `example-events.py` | Fetches first page of dividends, historical orders, transactions, and the list of CSV reports. | `example-events-response.json` |

## How to run

From the repo root:

```bash
pip install -e .
export TRADING212_API_KEY="your-key"
export TRADING212_API_SECRET="your-secret"
cd examples
python example-account.py
# etc.
```

See `examples/README.md` for more detail.
