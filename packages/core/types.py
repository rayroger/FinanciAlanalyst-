"""Shared Python dataclasses used across packages."""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional


@dataclass
class Transaction:
    """Canonical transaction representation (not SQLAlchemy ORM)."""

    plaid_transaction_id: str
    amount: float
    is_credit: bool
    date: date
    name: str
    merchant_name: Optional[str] = None
    category: Optional[str] = None
    plaid_category: Optional[str] = None
    pending: bool = False


@dataclass
class Account:
    """Canonical account representation."""

    plaid_account_id: str
    plaid_item_id: str
    institution_name: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    account_subtype: Optional[str] = None


@dataclass
class AnomalyItem:
    """A spending anomaly for a given category."""

    category: str
    current_month_spend: float
    previous_month_spend: float
    pct_change: float
    description: str


@dataclass
class InsightResult:
    """AI-generated financial insight response."""

    monthly_summary: str
    top_categories: list[dict] = field(default_factory=list)
    anomalies: list[AnomalyItem] = field(default_factory=list)
    recurring_subscriptions: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
