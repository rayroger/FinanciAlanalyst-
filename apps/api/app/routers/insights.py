"""Insights router: AI-generated financial insights."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import Transaction, User
from app.routers.auth import get_current_user
from app.schemas.schemas import InsightResult
from app.services.ai_service import AIService

router = APIRouter()


@router.get("", response_model=InsightResult)
async def get_insights(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InsightResult:
    """Return AI-generated insights for the authenticated user's recent transactions."""
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.desc())
        .limit(500)
    )
    transactions = list(result.scalars().all())

    svc = AIService()
    return await svc.generate_insights(transactions)
