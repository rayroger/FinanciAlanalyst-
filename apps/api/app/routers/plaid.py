"""Plaid router: link token, token exchange, and transaction sync."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import User
from app.routers.auth import get_current_user
from app.schemas.schemas import PlaidExchangeRequest, PlaidLinkTokenResponse
from app.services.plaid_service import PlaidService

router = APIRouter()


@router.post("/link-token", response_model=PlaidLinkTokenResponse)
async def create_link_token(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaidLinkTokenResponse:
    """Create a Plaid Link token for the authenticated user."""
    svc = PlaidService()
    result = await svc.create_link_token(user_id=str(current_user.id))
    return result


@router.post("/exchange-token", status_code=status.HTTP_201_CREATED)
async def exchange_token(
    payload: PlaidExchangeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Exchange a Plaid public_token for a stored (encrypted) access token."""
    svc = PlaidService()
    account = await svc.exchange_public_token(
        db=db,
        user_id=current_user.id,
        public_token=payload.public_token,
        institution_name=payload.institution_name,
    )
    return {"account_id": str(account.id), "institution_name": account.institution_name}


@router.post("/sync")
async def sync_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Sync the latest transactions from Plaid for all user accounts."""
    svc = PlaidService()
    count = await svc.sync_transactions(db=db, user_id=current_user.id)
    return {"synced": count}
