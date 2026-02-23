"""Plaid connector — thin wrapper around plaid-python for use across packages."""

import os
from typing import Any

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products


class PlaidConnector:
    """Standalone Plaid API wrapper, configured via environment variables.

    Environment variables required:
        PLAID_CLIENT_ID
        PLAID_SECRET
        PLAID_ENV  (sandbox | development | production)
    """

    _ENV_MAP = {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }

    def __init__(self) -> None:
        client_id = os.environ["PLAID_CLIENT_ID"]
        secret = os.environ["PLAID_SECRET"]
        env = os.environ.get("PLAID_ENV", "sandbox")

        configuration = plaid.Configuration(
            host=self._ENV_MAP.get(env, plaid.Environment.Sandbox),
            api_key={"clientId": client_id, "secret": secret},
        )
        self._api = plaid_api.PlaidApi(plaid.ApiClient(configuration))

    def create_link_token(self, user_id: str, client_name: str = "FinanciAlanalyst") -> dict:
        """Create a Link token for the Plaid Link flow."""
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name=client_name,
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = self._api.link_token_create(request)
        return {"link_token": response["link_token"], "expiration": str(response["expiration"])}

    def exchange_public_token(self, public_token: str) -> dict:
        """Exchange a public token for an access token and item ID.

        SECURITY: Never log or persist access_token in plaintext.
        """
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self._api.item_public_token_exchange(request)
        return {
            "access_token": response["access_token"],
            "item_id": response["item_id"],
        }

    def get_accounts(self, access_token: str) -> list[dict[str, Any]]:
        """Retrieve account details for a given access token."""
        from plaid.model.accounts_get_request import AccountsGetRequest
        response = self._api.accounts_get(AccountsGetRequest(access_token=access_token))
        return [dict(a) for a in response["accounts"]]

    def sync_transactions(
        self, access_token: str, cursor: str = ""
    ) -> dict[str, Any]:
        """Fetch new/updated transactions since the last cursor.

        Returns dict with keys: added, modified, removed, next_cursor, has_more.
        """
        request = TransactionsSyncRequest(access_token=access_token, cursor=cursor)
        response = self._api.transactions_sync(request)
        return {
            "added": response["added"],
            "modified": response["modified"],
            "removed": response["removed"],
            "next_cursor": response["next_cursor"],
            "has_more": response["has_more"],
        }
