"""Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ── Account ───────────────────────────────────────────────────────────────────

class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plaid_account_id: str
    institution_name: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    account_subtype: Optional[str] = None
    created_at: datetime


# ── Transaction ───────────────────────────────────────────────────────────────

class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    plaid_transaction_id: str
    amount: float
    is_credit: bool
    date: date
    merchant_name: Optional[str] = None
    name: str
    category: Optional[str] = None
    pending: bool


class TransactionFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category: Optional[str] = None
    limit: int = 100
    offset: int = 0


# ── Plaid ─────────────────────────────────────────────────────────────────────

class PlaidExchangeRequest(BaseModel):
    public_token: str
    institution_name: Optional[str] = None


class PlaidLinkTokenResponse(BaseModel):
    link_token: str
    expiration: str


# ── Insights ──────────────────────────────────────────────────────────────────

class AnomalyItem(BaseModel):
    category: str
    current_month_spend: float
    previous_month_spend: float
    pct_change: float
    description: str


class InsightResult(BaseModel):
    monthly_summary: str
    top_categories: list[dict]
    anomalies: list[AnomalyItem]
    recurring_subscriptions: list[str]
    generated_at: datetime
