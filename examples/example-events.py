"""
Example: Historical events endpoints (dividends, orders, transactions, reports).

Fetches first page of dividends, historical orders, transactions, and the reports list,
and saves the response to example-events-response.json.
Requires TRADING212_API_KEY and TRADING212_API_SECRET environment variables.
"""

import json
import os
from pathlib import Path

import trading212api


def main() -> None:
    api_key = os.environ.get("TRADING212_API_KEY")
    api_secret = os.environ.get("TRADING212_API_SECRET")
    if not api_key or not api_secret:
        print("Set TRADING212_API_KEY and TRADING212_API_SECRET environment variables.")
        raise SystemExit(1)

    client = trading212api.Trading212Client(
        api_key=api_key,
        api_secret=api_secret,
        base_url=trading212api.DEFAULT_LIVE_URL,
    )
    dividends = client.get_dividends(limit=5)
    historical_orders = client.get_historical_orders(limit=5)
    transactions = client.get_transactions(limit=5)
    reports = client.get_reports()

    data = {
        "dividends": dividends.model_dump(by_alias=True, exclude_none=True),
        "historical_orders": historical_orders.model_dump(by_alias=True, exclude_none=True),
        "transactions": transactions.model_dump(by_alias=True, exclude_none=True),
        "reports": [r.model_dump(by_alias=True, exclude_none=True) for r in reports],
    }
    out_path = Path(__file__).resolve().parent / "example-events-response.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
