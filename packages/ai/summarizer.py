"""GPT-4o finance summarizer — standalone package version."""

import json
import os
from collections import defaultdict
from datetime import datetime, timezone

from openai import OpenAI

from core.types import InsightResult, AnomalyItem, Transaction

_SYSTEM_PROMPT = """You are a concise personal finance analyst.
Given a JSON summary of a user's recent transactions, produce a JSON response with these keys:
- monthly_summary: plain-English paragraph (2-3 sentences) describing income vs spend
- top_categories: array of {category, total} objects sorted by total descending (top 5)
- anomalies: array of {category, current_month_spend, previous_month_spend, pct_change, description}
  only include categories with >15% change and >$20 absolute difference
- recurring_subscriptions: array of merchant name strings detected as monthly recurring charges

Return ONLY valid JSON, no markdown fences."""


class FinanceSummarizer:
    """Generates financial insights using OpenAI GPT-4o.

    Requires OPENAI_API_KEY environment variable.
    """

    def __init__(self) -> None:
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def summarize(self, transactions: list[Transaction]) -> InsightResult:
        """Generate an InsightResult from a list of Transaction dataclasses."""
        if not transactions:
            return InsightResult(
                monthly_summary="No transactions found.",
                generated_at=datetime.now(timezone.utc),
            )

        summary = self._build_summary(transactions)
        raw = self._call_openai(summary)
        return self._parse(raw)

    def _build_summary(self, transactions: list[Transaction]) -> dict:
        by_month: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        income_by_month: dict[str, float] = defaultdict(float)

        for txn in transactions:
            key = txn.date.strftime("%Y-%m")
            if txn.is_credit:
                income_by_month[key] += txn.amount
            else:
                by_month[key][txn.category or "Other"] += txn.amount

        return {
            "spend_by_month_category": {k: dict(v) for k, v in sorted(by_month.items())},
            "income_by_month": dict(sorted(income_by_month.items())),
            "transaction_count": len(transactions),
        }

    def _call_openai(self, summary: dict) -> str:
        response = self._client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(summary, indent=2)},
            ],
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"

    def _parse(self, raw: str) -> InsightResult:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {}

        anomalies = [
            AnomalyItem(**a)
            for a in data.get("anomalies", [])
            if all(k in a for k in ("category", "current_month_spend",
                                    "previous_month_spend", "pct_change", "description"))
        ]

        return InsightResult(
            monthly_summary=data.get("monthly_summary", ""),
            top_categories=data.get("top_categories", []),
            anomalies=anomalies,
            recurring_subscriptions=data.get("recurring_subscriptions", []),
            generated_at=datetime.now(timezone.utc),
        )
