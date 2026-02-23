"""Plaid service: link token creation, token exchange, transaction sync."""

import uuid
import logging
from typing import Any

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.models import Account, Transaction
from app.schemas.schemas import PlaidLinkTokenResponse
from app.services.categorizer import categorize_transaction

logger = logging.getLogger(__name__)


def _plaid_client() -> plaid_api.PlaidApi:
    """Build a configured Plaid API client."""
    env_map = {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }
    configuration = plaid.Configuration(
        host=env_map.get(settings.plaid_env, plaid.Environment.Sandbox),
        api_key={
            "clientId": settings.plaid_client_id,
            "secret": settings.plaid_secret,
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def _fernet() -> Fernet:
    return Fernet(settings.encryption_key.encode())


class PlaidService:
    """Wrapper around the Plaid API for link flow and transaction sync."""

    def __init__(self) -> None:
        self._client = _plaid_client()
        self._fernet = _fernet()

    def _encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def _decrypt(self, value: str) -> str:
        return self._fernet.decrypt(value.encode()).decode()

    async def create_link_token(self, user_id: str) -> PlaidLinkTokenResponse:
        """Create a Plaid Link token for the given user."""
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="FinanciAlanalyst",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = self._client.link_token_create(request)
        return PlaidLinkTokenResponse(
            link_token=response["link_token"],
            expiration=str(response["expiration"]),
        )

    async def exchange_public_token(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        public_token: str,
        institution_name: str | None = None,
    ) -> Account:
        """Exchange a Plaid public_token, encrypt and store the access token."""
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self._client.item_public_token_exchange(exchange_request)

        # SECURITY: never log access_token
        access_token: str = response["access_token"]
        item_id: str = response["item_id"]

        encrypted = self._encrypt(access_token)

        # Fetch account details from Plaid
        from plaid.model.accounts_get_request import AccountsGetRequest
        accounts_response = self._client.accounts_get(
            AccountsGetRequest(access_token=access_token)
        )
        plaid_accounts: list[Any] = accounts_response["accounts"]

        # Store first account (simplification — real apps store all)
        plaid_acct = plaid_accounts[0] if plaid_accounts else None

        account = Account(
            user_id=user_id,
            plaid_item_id=item_id,
            plaid_account_id=plaid_acct["account_id"] if plaid_acct else item_id,
            encrypted_access_token=encrypted,
            institution_name=institution_name,
            account_name=plaid_acct["name"] if plaid_acct else None,
            account_type=str(plaid_acct["type"]) if plaid_acct else None,
            account_subtype=str(plaid_acct["subtype"]) if plaid_acct else None,
        )
        db.add(account)
        await db.flush()
        return account

    async def sync_transactions(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        """Sync all new/updated transactions for every account owned by user_id."""
        result = await db.execute(
            select(Account).where(Account.user_id == user_id)
        )
        accounts = list(result.scalars().all())

        total_synced = 0
        for account in accounts:
            access_token = self._decrypt(account.encrypted_access_token)
            total_synced += await self._sync_account(db, account, access_token)

        return total_synced

    async def _sync_account(
        self, db: AsyncSession, account: Account, access_token: str
    ) -> int:
        """Run Plaid transactions/sync for a single account, handling pagination."""
        added_count = 0
        cursor = account.cursor or ""
        has_more = True

        while has_more:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor,
            )
            response = self._client.transactions_sync(request)
            has_more = response["has_more"]
            cursor = response["next_cursor"]

            for txn in response["added"]:
                existing = await db.execute(
                    select(Transaction).where(
                        Transaction.plaid_transaction_id == txn["transaction_id"]
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                amount: float = float(txn["amount"])
                is_credit = amount < 0
                category = categorize_transaction(
                    name=txn.get("name", ""),
                    merchant=txn.get("merchant_name"),
                    plaid_category=txn.get("personal_finance_category", {}).get("primary"),
                )

                db.add(
                    Transaction(
                        user_id=account.user_id,
                        account_id=account.id,
                        plaid_transaction_id=txn["transaction_id"],
                        amount=abs(amount),
                        is_credit=is_credit,
                        date=txn["date"],
                        merchant_name=txn.get("merchant_name"),
                        name=txn.get("name", ""),
                        category=category,
                        plaid_category=str(
                            txn.get("personal_finance_category", {}).get("primary", "")
                        ),
                        pending=txn.get("pending", False),
                    )
                )
                added_count += 1

        # Persist updated cursor
        account.cursor = cursor
        await db.flush()
        return added_count
