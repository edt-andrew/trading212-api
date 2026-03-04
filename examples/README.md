# Examples

Each script calls Trading 212 API endpoints and saves the JSON response to a file in this folder.

## Setup

1. Install the package from the repo root: `pip install -e .`
2. Set environment variables:
   - `TRADING212_API_KEY` — your API key
   - `TRADING212_API_SECRET` — your API secret

All examples use the live environment by default.

## Scripts

| Script | Endpoint(s) | Output file |
|--------|-------------|-------------|
| `example-account.py` | Account summary | `example-account-response.json` |
| `example-instrument.py` | Exchanges, instruments | `example-instrument-response.json` |
| `example-orders.py` | Pending orders | `example-orders-response.json` |
| `example-positions.py` | Open positions | `example-positions-response.json` |
| `example-events.py` | Dividends, historical orders, transactions, reports | `example-events-response.json` |

## Run

```bash
cd examples
python example-account.py
python example-instrument.py
# etc.
```
