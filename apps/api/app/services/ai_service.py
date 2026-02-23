"""AI service: GPT-4o powered financial insights and anomaly detection."""

import json
import logging
from collections import defaultdict
from datetime import datetime, timezone

from openai import AsyncOpenAI

from app.config import settings
from app.models.models import Transaction
from app.schemas.schemas import AnomalyItem, InsightResult

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a concise personal finance analyst. 
Given a JSON summary of a user's recent transactions, produce a JSON response with these keys:
- monthly_summary: plain-English paragraph (2-3 sentences) describing income vs spend
- top_categories: array of {category, total} objects sorted by total descending (top 5)
- anomalies: array of {category, current_month_spend, previous_month_spend, pct_change, description}
  only include categories with >15% change and >$20 absolute difference
- recurring_subscriptions: array of merchant name strings detected as monthly recurring charges

Return ONLY valid JSON, no markdown fences."""


class AIService:
    """Generates financial insights using OpenAI GPT-4o."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_insights(self, transactions: list[Transaction]) -> InsightResult:
        """Generate a full InsightResult from a list of ORM Transaction objects."""
        if not transactions:
            return InsightResult(
                monthly_summary="No transactions found. Connect a bank account to get started.",
                top_categories=[],
                anomalies=[],
                recurring_subscriptions=[],
                generated_at=datetime.now(timezone.utc),
            )

        summary_data = self._build_summary(transactions)
        raw = await self._call_openai(summary_data)
        return self._parse_response(raw)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _build_summary(self, transactions: list[Transaction]) -> dict:
        """Aggregate transactions into a compact dict for the AI prompt."""
        by_month: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for txn in transactions:
            month_key = txn.date.strftime("%Y-%m")
            cat = txn.category or "Uncategorized"
            if not txn.is_credit:
                by_month[month_key][cat] += float(txn.amount)

        # Total income per month
        income_by_month: dict[str, float] = defaultdict(float)
        for txn in transactions:
            if txn.is_credit:
                income_by_month[txn.date.strftime("%Y-%m")] += float(txn.amount)

        return {
            "spend_by_month_category": {k: dict(v) for k, v in sorted(by_month.items())},
            "income_by_month": dict(sorted(income_by_month.items())),
            "transaction_count": len(transactions),
        }

    async def _call_openai(self, summary: dict) -> str:
        """Send the aggregated summary to GPT-4o and return raw JSON string."""
        prompt = json.dumps(summary, indent=2)
        response = await self._client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"

    def _parse_response(self, raw: str) -> InsightResult:
        """Parse the GPT-4o JSON response into an InsightResult."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI response as JSON")
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
