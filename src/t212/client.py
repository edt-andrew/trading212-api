"""
Trading 212 REST API client.

Uses HTTP Basic authentication (API key as username, API secret as password).
Supports demo and live base URLs.
"""

from __future__ import annotations

import time
from typing import Optional, Union

import httpx
from pydantic import TypeAdapter

from .models import (
    AccountSummary,
    EnqueuedReportResponse,
    Exchange,
    LimitOrderRequest,
    MarketOrderRequest,
    Order,
    PaginatedDividends,
    PaginatedHistoricalOrders,
    PaginatedTransactions,
    Position,
    PublicReportRequest,
    ReportResponse,
    StopLimitOrderRequest,
    StopOrderRequest,
    TradableInstrument,
)

DEFAULT_DEMO_URL = "https://demo.trading212.com/api/v0"
DEFAULT_LIVE_URL = "https://live.trading212.com/api/v0"


def _parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


class RateLimitInfo:
    """
    Rate limit information from the last API response headers.

    Attributes:
        limit: Total requests allowed in the current period.
        period: Duration of the period in seconds.
        remaining: Requests left in the current period.
        reset: Unix timestamp when the limit will reset.
        used: Requests already made in the current period.
    """

    __slots__ = ("limit", "period", "remaining", "reset", "used")

    def __init__(
        self,
        limit: Optional[int] = None,
        period: Optional[int] = None,
        remaining: Optional[int] = None,
        reset: Optional[int] = None,
        used: Optional[int] = None,
    ):
        self.limit = limit
        self.period = period
        self.remaining = remaining
        self.reset = reset
        self.used = used

    @classmethod
    def from_headers(cls, headers: httpx.Headers) -> "RateLimitInfo":
        return cls(
            limit=_parse_int(headers.get("x-ratelimit-limit")),
            period=_parse_int(headers.get("x-ratelimit-period")),
            remaining=_parse_int(headers.get("x-ratelimit-remaining")),
            reset=_parse_int(headers.get("x-ratelimit-reset")),
            used=_parse_int(headers.get("x-ratelimit-used")),
        )


class Trading212APIError(Exception):
    """Raised when the API returns an error response."""

    def __init__(self, message: str, status_code: Optional[int] = None, body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class Trading212Client:
    """
    Client for the Trading 212 Public API (Invest and Stocks ISA).

    Usage:
        client = Trading212Client(api_key="...", api_secret="...")
        summary = client.get_account_summary()
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        *,
        base_url: str = DEFAULT_DEMO_URL,
        timeout: float = 30.0,
        http_client: Optional[httpx.Client] = None,
        retry_on_429: bool = False,
    ):
        self._base_url = base_url.rstrip("/")
        self._auth = (api_key, api_secret)
        self._timeout = timeout
        self._retry_on_429 = retry_on_429
        self._client = http_client or httpx.Client(
            auth=self._auth,
            timeout=timeout,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        self._own_client = http_client is None
        self._last_rate_limit: Optional[RateLimitInfo] = None

    def close(self) -> None:
        if self._own_client and self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> Trading212Client:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @property
    def last_rate_limit(self) -> Optional[RateLimitInfo]:
        """Rate limit information from the last API response, or None if no request has been made yet."""
        return self._last_rate_limit

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        _retry_after_429: bool = True,
    ) -> httpx.Response:
        url = f"{self._base_url}{path}" if path.startswith("/") else f"{self._base_url}/{path}"
        response = self._client.request(method, url, params=params, json=json)
        self._last_rate_limit = RateLimitInfo.from_headers(response.headers)
        if response.status_code == 429 and self._retry_on_429 and _retry_after_429:
            reset = self._last_rate_limit.reset
            if reset is not None:
                wait = max(0.0, reset - time.time()) + 0.5
                time.sleep(min(wait, 60.0))
                return self._request(
                    method, path, params=params, json=json, _retry_after_429=False
                )
        if response.status_code >= 400:
            raise Trading212APIError(
                f"API error: {response.status_code}",
                status_code=response.status_code,
                body=response.text,
            )
        return response

    def _get(self, path: str, params: Optional[dict] = None) -> httpx.Response:
        return self._request("GET", path, params=params)

    def _get_by_next_page_path(self, next_page_path: str) -> httpx.Response:
        """Request the next page using the path returned in nextPagePath."""
        path = next_page_path.removeprefix("/api/v0").lstrip("/")
        return self._get(f"/{path}" if path else "/")

    def _post(self, path: str, json: Optional[dict] = None) -> httpx.Response:
        return self._request("POST", path, json=json)

    def _delete(self, path: str) -> httpx.Response:
        return self._request("DELETE", path)

    # -------------------------------------------------------------------------
    # Accounts
    # -------------------------------------------------------------------------

    def get_account_summary(self) -> AccountSummary:
        """Get account summary (cash, investments, total value). Rate limit: 1 req / 5s."""
        r = self._get("/equity/account/summary")
        return AccountSummary.model_validate(r.json())

    # -------------------------------------------------------------------------
    # Instruments / metadata
    # -------------------------------------------------------------------------

    def get_exchanges(self) -> list[Exchange]:
        """Get all accessible exchanges and working schedules. Rate limit: 1 req / 30s."""
        r = self._get("/equity/metadata/exchanges")
        return TypeAdapter(list[Exchange]).validate_python(r.json())

    def get_instruments(self) -> list[TradableInstrument]:
        """Get all available instruments. Rate limit: 1 req / 50s."""
        r = self._get("/equity/metadata/instruments")
        return TypeAdapter(list[TradableInstrument]).validate_python(r.json())

    # -------------------------------------------------------------------------
    # Orders
    # -------------------------------------------------------------------------

    def get_pending_orders(self) -> list[Order]:
        """Get all pending (active) orders. Rate limit: 1 req / 5s."""
        r = self._get("/equity/orders")
        return TypeAdapter(list[Order]).validate_python(r.json())

    def get_order_by_id(self, order_id: int) -> Order:
        """Get a single pending order by ID. Rate limit: 1 req / 1s."""
        r = self._get(f"/equity/orders/{order_id}")
        return Order.model_validate(r.json())

    def place_limit_order(self, request: LimitOrderRequest) -> Order:
        """Place a limit order. Rate limit: 1 req / 2s."""
        r = self._post("/equity/orders/limit", json=request.model_dump(by_alias=True, exclude_none=True))
        return Order.model_validate(r.json())

    def place_market_order(self, request: MarketOrderRequest) -> Order:
        """Place a market order. Rate limit: 50 req / 1m."""
        r = self._post("/equity/orders/market", json=request.model_dump(by_alias=True, exclude_none=True))
        return Order.model_validate(r.json())

    def place_stop_order(self, request: StopOrderRequest) -> Order:
        """Place a stop order. Rate limit: 1 req / 2s."""
        r = self._post("/equity/orders/stop", json=request.model_dump(by_alias=True, exclude_none=True))
        return Order.model_validate(r.json())

    def place_stop_limit_order(self, request: StopLimitOrderRequest) -> Order:
        """Place a stop-limit order. Rate limit: 1 req / 2s."""
        r = self._post("/equity/orders/stop_limit", json=request.model_dump(by_alias=True, exclude_none=True))
        return Order.model_validate(r.json())

    def cancel_order(self, order_id: int) -> None:
        """Cancel a pending order. Rate limit: 50 req / 1m."""
        self._delete(f"/equity/orders/{order_id}")

    # -------------------------------------------------------------------------
    # Positions
    # -------------------------------------------------------------------------

    def get_positions(self) -> list[Position]:
        """Get all open positions. Rate limit: 1 req / 1s."""
        r = self._get("/equity/positions")
        return TypeAdapter(list[Position]).validate_python(r.json())

    # -------------------------------------------------------------------------
    # Historical: dividends, orders, transactions
    # -------------------------------------------------------------------------

    def get_dividends(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[Union[int, str]] = None,
        ticker: Optional[str] = None,
    ) -> PaginatedDividends:
        """Get paid-out dividends. Rate limit: 6 req / 1m."""
        params: dict = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if ticker is not None:
            params["ticker"] = ticker
        r = self._get("/equity/history/dividends", params=params or None)
        return PaginatedDividends.model_validate(r.json())

    def get_all_dividends(
        self,
        *,
        limit: Optional[int] = None,
        ticker: Optional[str] = None,
    ) -> PaginatedDividends:
        """Get all paid-out dividends by following nextPagePath. Returns a single object with all items."""
        all_items: list = []
        page = self.get_dividends(limit=limit, ticker=ticker)
        all_items.extend(page.items)
        while page.next_page_path:
            r = self._get_by_next_page_path(page.next_page_path)
            page = PaginatedDividends.model_validate(r.json())
            all_items.extend(page.items)
        return PaginatedDividends(items=all_items, next_page_path=None)

    def get_historical_orders(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[Union[int, str]] = None,
        ticker: Optional[str] = None,
    ) -> PaginatedHistoricalOrders:
        """Get historical orders. Rate limit: 6 req / 1m."""
        params: dict = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if ticker is not None:
            params["ticker"] = ticker
        r = self._get("/equity/history/orders", params=params or None)
        return PaginatedHistoricalOrders.model_validate(r.json())

    def get_all_historical_orders(
        self,
        *,
        limit: Optional[int] = None,
        ticker: Optional[str] = None,
    ) -> PaginatedHistoricalOrders:
        """Get all historical orders by following nextPagePath. Returns a single object with all items."""
        all_items: list = []
        page = self.get_historical_orders(limit=limit, ticker=ticker)
        all_items.extend(page.items)
        while page.next_page_path:
            r = self._get_by_next_page_path(page.next_page_path)
            page = PaginatedHistoricalOrders.model_validate(r.json())
            all_items.extend(page.items)
        return PaginatedHistoricalOrders(items=all_items, next_page_path=None)

    def get_transactions(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        time: Optional[str] = None,
    ) -> PaginatedTransactions:
        """Get account transactions. Rate limit: 6 req / 1m."""
        params: dict = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if time is not None:
            params["time"] = time
        r = self._get("/equity/history/transactions", params=params or None)
        return PaginatedTransactions.model_validate(r.json())

    def get_all_transactions(
        self,
        *,
        limit: Optional[int] = None,
        time: Optional[str] = None,
    ) -> PaginatedTransactions:
        """Get all transactions by following nextPagePath. Returns a single object with all items."""
        all_items: list = []
        page = self.get_transactions(limit=limit, time=time)
        all_items.extend(page.items)
        while page.next_page_path:
            r = self._get_by_next_page_path(page.next_page_path)
            page = PaginatedTransactions.model_validate(r.json())
            all_items.extend(page.items)
        return PaginatedTransactions(items=all_items, next_page_path=None)

    # -------------------------------------------------------------------------
    # Reports (CSV exports)
    # -------------------------------------------------------------------------

    def get_reports(self) -> list[ReportResponse]:
        """List generated CSV reports and their status. Rate limit: 1 req / 1m."""
        r = self._get("/equity/history/exports")
        return TypeAdapter(list[ReportResponse]).validate_python(r.json())

    def request_report(self, request: PublicReportRequest) -> EnqueuedReportResponse:
        """Request a CSV report (async). Poll get_reports() for status. Rate limit: 1 req / 30s."""
        r = self._post("/equity/history/exports", json=request.model_dump(by_alias=True, exclude_none=True))
        return EnqueuedReportResponse.model_validate(r.json())
