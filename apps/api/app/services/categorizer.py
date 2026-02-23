"""Rule-based transaction categorizer used before AI enrichment."""

from typing import Optional

MERCHANT_CATEGORY_MAP: dict[str, str] = {
    # Food & Dining
    "mcdonald": "Food & Dining",
    "starbucks": "Food & Dining",
    "chipotle": "Food & Dining",
    "subway": "Food & Dining",
    "doordash": "Food & Dining",
    "ubereats": "Food & Dining",
    "grubhub": "Food & Dining",
    "postmates": "Food & Dining",
    "whole foods": "Groceries",
    "trader joe": "Groceries",
    "kroger": "Groceries",
    "safeway": "Groceries",
    "walmart": "Groceries",
    "costco": "Groceries",
    "target": "Shopping",
    # Transport
    "uber": "Transport",
    "lyft": "Transport",
    "metro": "Transport",
    "mta": "Transport",
    "gas station": "Gas & Fuel",
    "shell": "Gas & Fuel",
    "chevron": "Gas & Fuel",
    "exxon": "Gas & Fuel",
    # Utilities
    "electric": "Utilities",
    "water bill": "Utilities",
    "internet": "Utilities",
    "comcast": "Utilities",
    "verizon": "Utilities",
    "at&t": "Utilities",
    # Subscriptions
    "netflix": "Subscriptions",
    "spotify": "Subscriptions",
    "hulu": "Subscriptions",
    "amazon prime": "Subscriptions",
    "apple": "Subscriptions",
    "google play": "Subscriptions",
    "youtube premium": "Subscriptions",
    # Health
    "cvs": "Health",
    "walgreens": "Health",
    "pharmacy": "Health",
    "doctor": "Health",
    "hospital": "Health",
    "gym": "Health & Fitness",
    "planet fitness": "Health & Fitness",
    # Travel
    "hotel": "Travel",
    "airbnb": "Travel",
    "airline": "Travel",
    "delta": "Travel",
    "united": "Travel",
    "southwest": "Travel",
    # Shopping
    "amazon": "Shopping",
    "ebay": "Shopping",
    "etsy": "Shopping",
    "best buy": "Shopping",
    # Entertainment
    "movie": "Entertainment",
    "cinema": "Entertainment",
    "ticketmaster": "Entertainment",
    "steam": "Entertainment",
    # Finance
    "atm": "ATM & Cash",
    "bank fee": "Bank Fees",
    "interest charge": "Bank Fees",
    # Income
    "payroll": "Income",
    "direct deposit": "Income",
    "zelle": "Transfers",
    "venmo": "Transfers",
    "paypal": "Transfers",
}

# Map Plaid personal_finance_category primary values to our labels
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
    "PERSONAL_CARE": "Personal Care",
    "HOME_IMPROVEMENT": "Home",
    "GENERAL_SERVICES": "Services",
    "RENT_AND_UTILITIES": "Housing",
    "LOAN_PAYMENTS": "Loan Payments",
    "TRANSFER_IN": "Income",
    "TRANSFER_OUT": "Transfers",
    "INCOME": "Income",
    "BANK_FEES": "Bank Fees",
    "SUBSCRIPTION": "Subscriptions",
}


def categorize_transaction(
    name: str,
    merchant: Optional[str] = None,
    plaid_category: Optional[str] = None,
) -> str:
    """Categorize a transaction using merchant name lookup and Plaid category fallback.

    Priority:
    1. Plaid personal_finance_category primary value
    2. Keyword match on merchant / transaction name
    3. Fallback to "Other"
    """
    # 1. Plaid category
    if plaid_category:
        mapped = PLAID_CATEGORY_MAP.get(plaid_category.upper())
        if mapped:
            return mapped

    # 2. Keyword match (case-insensitive)
    search_text = f"{merchant or ''} {name}".lower()
    for keyword, category in MERCHANT_CATEGORY_MAP.items():
        if keyword in search_text:
            return category

    return "Other"
