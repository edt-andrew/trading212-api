"""
Pydantic models for Trading 212 API request and response payloads.

All models use camelCase aliases for JSON (de)serialization to match the API.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


# ---------------------------------------------------------------------------
# Enums (API string literals)
# ---------------------------------------------------------------------------


class TimeValidity(str, Enum):
    """Order time validity."""

    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    LOCAL = "LOCAL"
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"
    NEW = "NEW"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    REPLACING = "REPLACING"
    REPLACED = "REPLACED"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    STOP = "STOP"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"


class TransactionType(str, Enum):
    WITHDRAW = "WITHDRAW"
    DEPOSIT = "DEPOSIT"
    FEE = "FEE"
    TRANSFER = "TRANSFER"


class ReportStatus(str, Enum):
    QUEUED = "Queued"
    PROCESSING = "Processing"
    RUNNING = "Running"
    CANCELED = "Canceled"
    FAILED = "Failed"
    FINISHED = "Finished"


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------


class Cash(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    available_to_trade: Optional[float] = None
    in_pies: Optional[float] = None
    reserved_for_orders: Optional[float] = None


class Investments(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    current_value: Optional[float] = None
    realized_profit_loss: Optional[float] = None
    total_cost: Optional[float] = None
    unrealized_profit_loss: Optional[float] = None


class AccountSummary(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    cash: Optional[Cash] = None
    currency: Optional[str] = None
    id: Optional[int] = None
    investments: Optional[Investments] = None
    total_value: Optional[float] = None


# ---------------------------------------------------------------------------
# Instruments & metadata
# ---------------------------------------------------------------------------


class TimeEvent(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    date: Optional[str] = None
    type: Optional[str] = None


class WorkingSchedule(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: Optional[int] = None
    time_events: Optional[list[TimeEvent]] = None


class Exchange(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: Optional[int] = None
    name: Optional[str] = None
    working_schedules: Optional[list[WorkingSchedule]] = None


class Instrument(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    currency: Optional[str] = None
    isin: Optional[str] = None
    name: Optional[str] = None
    ticker: Optional[str] = None


class TradableInstrument(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    added_on: Optional[str] = None
    currency_code: Optional[str] = None
    extended_hours: Optional[bool] = None
    isin: Optional[str] = None
    max_open_quantity: Optional[float] = None
    name: Optional[str] = None
    short_name: Optional[str] = None
    ticker: Optional[str] = None
    type: Optional[str] = None
    working_schedule_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Orders (request bodies)
# ---------------------------------------------------------------------------


class LimitOrderRequest(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    ticker: str
    quantity: float
    limit_price: float
    time_validity: Optional[TimeValidity] = TimeValidity.DAY


class MarketOrderRequest(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    ticker: str
    quantity: float
    extended_hours: bool = False


class StopOrderRequest(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    ticker: str
    quantity: float
    stop_price: float
    time_validity: Optional[TimeValidity] = TimeValidity.DAY


class StopLimitOrderRequest(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    ticker: str
    quantity: float
    stop_price: float
    limit_price: float
    time_validity: Optional[TimeValidity] = TimeValidity.DAY


# ---------------------------------------------------------------------------
# Order (response)
# ---------------------------------------------------------------------------


class Order(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: Optional[int] = None
    ticker: Optional[str] = None
    currency: Optional[str] = None
    quantity: Optional[float] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    side: Optional[OrderSide] = None
    status: Optional[OrderStatus] = None
    type: Optional[OrderType] = None
    instrument: Optional[Instrument] = None
    created_at: Optional[str] = None
    filled_quantity: Optional[float] = None
    filled_value: Optional[float] = None
    value: Optional[float] = None
    extended_hours: Optional[bool] = None
    time_in_force: Optional[str] = None
    strategy: Optional[str] = None
    initiated_from: Optional[str] = None


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


class PositionWalletImpact(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    currency: Optional[str] = None
    current_value: Optional[float] = None
    fx_impact: Optional[float] = None
    total_cost: Optional[float] = None
    unrealized_profit_loss: Optional[float] = None


class Position(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    instrument: Optional[Instrument] = None
    quantity: Optional[float] = None
    average_price_paid: Optional[float] = None
    current_price: Optional[float] = None
    quantity_available_for_trading: Optional[float] = None
    quantity_in_pies: Optional[float] = None
    created_at: Optional[str] = None
    wallet_impact: Optional[PositionWalletImpact] = None


# ---------------------------------------------------------------------------
# Historical: Fill, Tax, etc.
# ---------------------------------------------------------------------------


class Tax(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    charged_at: Optional[str] = None
    currency: Optional[str] = None
    name: Optional[str] = None
    quantity: Optional[float] = None


class FillWalletImpact(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    currency: Optional[str] = None
    fx_rate: Optional[float] = None
    net_value: Optional[float] = None
    realised_profit_loss: Optional[float] = None
    taxes: Optional[list[Tax]] = None


class Fill(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: Optional[int] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    filled_at: Optional[str] = None
    type: Optional[str] = None
    trading_method: Optional[str] = None
    wallet_impact: Optional[FillWalletImpact] = None


class HistoricalOrder(BaseModel):
    """Historical order with fill details."""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    order: Optional[Order] = None
    fill: Optional[Fill] = None


# ---------------------------------------------------------------------------
# History: dividends, transactions
# ---------------------------------------------------------------------------


class HistoryDividendItem(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    amount: Optional[float] = None
    amount_in_euro: Optional[float] = None
    currency: Optional[str] = None
    gross_amount_per_share: Optional[float] = None
    instrument: Optional[Instrument] = None
    paid_on: Optional[str] = None
    quantity: Optional[float] = None
    reference: Optional[str] = None
    ticker: Optional[str] = None
    ticker_currency: Optional[str] = None
    type: Optional[str] = None


class HistoryTransactionItem(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    amount: Optional[float] = None
    currency: Optional[str] = None
    date_time: Optional[str] = None
    reference: Optional[str] = None
    type: Optional[TransactionType] = None


# ---------------------------------------------------------------------------
# Paginated responses
# ---------------------------------------------------------------------------


class PaginatedHistoricalOrders(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    items: list[HistoricalOrder] = Field(default_factory=list)
    next_page_path: Optional[str] = None


class PaginatedDividends(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    items: list[HistoryDividendItem] = Field(default_factory=list)
    next_page_path: Optional[str] = None


class PaginatedTransactions(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    items: list[HistoryTransactionItem] = Field(default_factory=list)
    next_page_path: Optional[str] = None


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


class ReportDataIncluded(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    include_dividends: Optional[bool] = None
    include_interest: Optional[bool] = None
    include_orders: Optional[bool] = None
    include_transactions: Optional[bool] = None


class PublicReportRequest(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    time_from: Optional[str] = None  # date-time
    time_to: Optional[str] = None  # date-time
    data_included: Optional[ReportDataIncluded] = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    report_id: Optional[int] = None
    status: Optional[ReportStatus] = None
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    data_included: Optional[ReportDataIncluded] = None
    download_link: Optional[str] = None


class EnqueuedReportResponse(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    report_id: Optional[int] = None
