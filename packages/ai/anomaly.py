"""Anomaly detection: flag unusual spending vs historical average."""

from collections import defaultdict
from datetime import date

from core.types import AnomalyItem, Transaction

# Percentage change assigned to a brand-new spending category with no prior history (100%)
NEW_CATEGORY_PCT_CHANGE: float = 1.0


def detect_anomalies(
    transactions: list[Transaction],
    pct_threshold: float = 0.15,
    abs_threshold: float = 20.0,
) -> list[AnomalyItem]:
    """Detect categories where current month spend differs significantly from prior months.

    Args:
        transactions: List of Transaction dataclasses.
        pct_threshold: Minimum fractional change to flag (default 15%).
        abs_threshold: Minimum absolute dollar change to flag (default $20).

    Returns:
        List of AnomalyItem for each flagged category.
    """
    by_month: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for txn in transactions:
        if txn.is_credit:
            continue
        key = txn.date.strftime("%Y-%m")
        cat = txn.category or "Other"
        by_month[key][cat] += txn.amount

    if len(by_month) < 2:
        return []

    sorted_months = sorted(by_month.keys())
    current_month = sorted_months[-1]
    prior_months = sorted_months[:-1]

    # Compute per-category average for prior months
    all_categories = {cat for month in prior_months for cat in by_month[month]}
    all_categories.update(by_month[current_month].keys())

    anomalies: list[AnomalyItem] = []
    for cat in sorted(all_categories):
        prior_totals = [by_month[m].get(cat, 0.0) for m in prior_months]
        avg_prior = sum(prior_totals) / len(prior_totals) if prior_totals else 0.0
        current = by_month[current_month].get(cat, 0.0)

        if avg_prior == 0 and current == 0:
            continue

        # New category with no prior history — treat as 100% increase
        if avg_prior == 0:
            pct_change = NEW_CATEGORY_PCT_CHANGE
        else:
            pct_change = (current - avg_prior) / avg_prior

        abs_change = abs(current - avg_prior)

        if abs(pct_change) >= pct_threshold and abs_change >= abs_threshold:
            direction = "up" if pct_change > 0 else "down"
            anomalies.append(
                AnomalyItem(
                    category=cat,
                    current_month_spend=round(current, 2),
                    previous_month_spend=round(avg_prior, 2),
                    pct_change=round(pct_change * 100, 1),
                    description=(
                        f"{cat} is {direction} {abs(pct_change) * 100:.0f}% "
                        f"vs prior average (${avg_prior:.0f} → ${current:.0f})"
                    ),
                )
            )

    return sorted(anomalies, key=lambda a: abs(a.pct_change), reverse=True)
