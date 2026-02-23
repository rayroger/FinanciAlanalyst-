"""Unit tests for the rule-based transaction categorizer."""

import pytest
from app.services.categorizer import categorize_transaction


@pytest.mark.parametrize(
    "name, merchant, plaid_category, expected",
    [
        # Plaid category takes priority
        ("Some purchase", None, "FOOD_AND_DRINK", "Food & Dining"),
        ("Some purchase", None, "GROCERIES", "Groceries"),
        ("Some purchase", None, "TRANSPORTATION", "Transport"),
        ("Some purchase", None, "SUBSCRIPTION", "Subscriptions"),
        # Merchant keyword match
        ("Starbucks Coffee", "Starbucks", None, "Food & Dining"),
        ("NETFLIX.COM", "Netflix", None, "Subscriptions"),
        ("SPOTIFY USA", "Spotify", None, "Subscriptions"),
        ("UBER TRIP", "Uber", None, "Transport"),
        ("WHOLE FOODS #123", "Whole Foods", None, "Groceries"),
        ("SHELL GAS STATION", None, None, "Gas & Fuel"),
        ("Planet Fitness Dues", "Planet Fitness", None, "Health & Fitness"),
        ("Amazon.com order", "Amazon", None, "Shopping"),
        # Name-only match when no merchant
        ("doordash delivery", None, None, "Food & Dining"),
        ("delta airlines ticket", None, None, "Travel"),
        # Unknown → Other
        ("Random store #99", None, None, "Other"),
        ("ZXQR LLC PAYMENT", None, None, "Other"),
        # Plaid category unknown falls back to keyword
        ("Starbucks", "Starbucks", "UNKNOWN_CATEGORY", "Food & Dining"),
        # Income
        ("PAYROLL DEPOSIT", None, "INCOME", "Income"),
    ],
)
def test_categorize_transaction(
    name: str,
    merchant: str | None,
    plaid_category: str | None,
    expected: str,
) -> None:
    result = categorize_transaction(name=name, merchant=merchant, plaid_category=plaid_category)
    assert result == expected, f"Expected '{expected}' for '{name}', got '{result}'"


def test_categorize_empty_strings() -> None:
    assert categorize_transaction(name="", merchant="", plaid_category="") == "Other"


def test_categorize_case_insensitive() -> None:
    assert categorize_transaction(name="MCDONALD'S #123") == "Food & Dining"
    assert categorize_transaction(name="mcdonald's drivethru") == "Food & Dining"


def test_plaid_category_overrides_keyword() -> None:
    # Even if name contains "amazon" (Shopping), Plaid says GROCERIES
    result = categorize_transaction(
        name="amazon fresh order", merchant="Amazon", plaid_category="GROCERIES"
    )
    assert result == "Groceries"
