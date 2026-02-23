"""Shared transaction categorizer (mirrors app/services/categorizer.py for package use)."""

from typing import Optional

MERCHANT_CATEGORY_MAP: dict[str, str] = {
    "mcdonald": "Food & Dining",
    "starbucks": "Food & Dining",
    "chipotle": "Food & Dining",
    "doordash": "Food & Dining",
    "ubereats": "Food & Dining",
    "grubhub": "Food & Dining",
    "whole foods": "Groceries",
    "trader joe": "Groceries",
    "kroger": "Groceries",
    "safeway": "Groceries",
    "walmart": "Groceries",
    "costco": "Groceries",
    "target": "Shopping",
    "uber": "Transport",
    "lyft": "Transport",
    "mta": "Transport",
    "shell": "Gas & Fuel",
    "chevron": "Gas & Fuel",
    "exxon": "Gas & Fuel",
    "comcast": "Utilities",
    "verizon": "Utilities",
    "netflix": "Subscriptions",
    "spotify": "Subscriptions",
    "hulu": "Subscriptions",
    "amazon prime": "Subscriptions",
    "apple": "Subscriptions",
    "cvs": "Health",
    "walgreens": "Health",
    "gym": "Health & Fitness",
    "planet fitness": "Health & Fitness",
    "hotel": "Travel",
    "airbnb": "Travel",
    "delta": "Travel",
    "amazon": "Shopping",
    "payroll": "Income",
    "direct deposit": "Income",
    "venmo": "Transfers",
    "zelle": "Transfers",
}

PLAID_CATEGORY_MAP: dict[str, str] = {
    "FOOD_AND_DRINK": "Food & Dining",
    "GROCERIES": "Groceries",
    "GENERAL_MERCHANDISE": "Shopping",
    "TRANSPORTATION": "Transport",
    "GAS_STATIONS": "Gas & Fuel",
    "UTILITIES": "Utilities",
    "ENTERTAINMENT": "Entertainment",
    "TRAVEL": "Travel",
    "MEDICAL": "Health",
    "SUBSCRIPTION": "Subscriptions",
    "TRANSFER_IN": "Income",
    "INCOME": "Income",
}


def categorize_transaction(
    name: str,
    merchant: Optional[str] = None,
    plaid_category: Optional[str] = None,
) -> str:
    """Categorize a transaction; Plaid category takes priority over keyword match."""
    if plaid_category:
        mapped = PLAID_CATEGORY_MAP.get(plaid_category.upper())
        if mapped:
            return mapped

    search_text = f"{merchant or ''} {name}".lower()
    for keyword, category in MERCHANT_CATEGORY_MAP.items():
        if keyword in search_text:
            return category

    return "Other"
