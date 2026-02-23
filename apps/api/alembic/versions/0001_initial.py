"""Initial migration: create users, accounts, transactions tables.

Revision ID: 0001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("plaid_item_id", sa.String(255), nullable=False),
        sa.Column("plaid_account_id", sa.String(255), nullable=False, unique=True),
        sa.Column("encrypted_access_token", sa.Text(), nullable=False),
        sa.Column("institution_name", sa.String(255), nullable=True),
        sa.Column("account_name", sa.String(255), nullable=True),
        sa.Column("account_type", sa.String(64), nullable=True),
        sa.Column("account_subtype", sa.String(64), nullable=True),
        sa.Column("cursor", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("plaid_transaction_id", sa.String(255), nullable=False, unique=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("is_credit", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("merchant_name", sa.String(255), nullable=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("category", sa.String(128), nullable=True),
        sa.Column("plaid_category", sa.String(255), nullable=True),
        sa.Column("pending", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_date", "transactions", ["date"])
    op.create_index("ix_transactions_category", "transactions", ["category"])


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("accounts")
    op.drop_table("users")
