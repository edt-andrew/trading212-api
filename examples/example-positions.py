"""
Example: Positions endpoint.

Fetches all open positions and saves the response to example-positions-response.json.
Requires TRADING212_API_KEY and TRADING212_API_SECRET environment variables.
"""

import json
import os
from pathlib import Path

import t212


def main() -> None:
    api_key = os.environ.get("TRADING212_API_KEY")
    api_secret = os.environ.get("TRADING212_API_SECRET")
    if not api_key or not api_secret:
        print("Set TRADING212_API_KEY and TRADING212_API_SECRET environment variables.")
        raise SystemExit(1)

    client = t212.Trading212Client(
        api_key=api_key,
        api_secret=api_secret,
        base_url=t212.DEFAULT_DEMO_URL,
    )
    positions = client.get_positions()
    data = [p.model_dump(by_alias=True, exclude_none=True) for p in positions]
    out_path = Path(__file__).resolve().parent / "example-positions-response.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
