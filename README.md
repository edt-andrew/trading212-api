# pyt212

Python wrapper for the **Trading 212 REST API** (Invest and Stocks ISA accounts).

- **Install:** `pip install pyt212` (from [PyPI](https://pypi.org/project/pyt212/))
- **Import:** `import t212`

## Requirements

- Python 3.10+
- Trading 212 API key and secret (from the [Trading 212 app](https://helpcentre.trading212.com/hc/en-us/articles/14584770928157-Trading-212-API-key))

## Quick start

```python
import t212

# Use demo (paper) or live environment
client = t212.Trading212Client(
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    base_url=t212.DEFAULT_DEMO_URL,  # or DEFAULT_LIVE_URL
)

# Account
summary = client.get_account_summary()
print(summary.currency, summary.total_value)

# Pending orders and positions
orders = client.get_pending_orders()
positions = client.get_positions()

# Place a limit buy order (positive quantity = buy)
from t212 import LimitOrderRequest, TimeValidity
order = client.place_limit_order(
    LimitOrderRequest(ticker="AAPL_US_EQ", quantity=1.0, limit_price=150.0, time_validity=TimeValidity.DAY)
)
```

## API coverage

- **Accounts:** `get_account_summary()`
- **Instruments:** `get_exchanges()`, `get_instruments()`
- **Orders:** `get_pending_orders()`, `get_order_by_id()`, `place_limit_order()`, `place_market_order()`, `place_stop_order()`, `place_stop_limit_order()`, `cancel_order()`
- **Positions:** `get_positions()`
- **History:** `get_dividends()`, `get_historical_orders()`, `get_transactions()`, `get_reports()`, `request_report()`

All request and response payloads use **Pydantic** models. Paginated endpoints return objects with `items` and `next_page_path`; use `get_all_dividends()`, `get_all_historical_orders()`, and `get_all_transactions()` to fetch all pages in one call.

**Rate limits:** The client exposes the last response’s rate limit headers as `client.last_rate_limit` (`t212.RateLimitInfo`: `limit`, `period`, `remaining`, `reset`, `used`). Optional `retry_on_429=True` in the constructor will wait until the limit resets and retry once on 429.

## Environments

- **Demo (paper):** `https://demo.trading212.com/api/v0` — `t212.DEFAULT_DEMO_URL`
- **Live:** `https://live.trading212.com/api/v0` — `t212.DEFAULT_LIVE_URL`

## Documentation

- [Trading 212 API Terms](https://www.trading212.com/legal-documentation/API-Terms_EN.pdf)

## License

MIT
