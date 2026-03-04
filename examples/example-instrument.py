"""
Example: Instrument / metadata endpoints.

Fetches exchanges and instruments and saves the response to example-instrument-response.json.
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
    exchanges = client.get_exchanges()
    instruments = client.get_instruments()
    data = {
        "exchanges": [e.model_dump(by_alias=True, exclude_none=True) for e in exchanges],
        "instruments": [i.model_dump(by_alias=True, exclude_none=True) for i in instruments],
    }
    out_path = Path(__file__).resolve().parent / "example-instrument-response.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
