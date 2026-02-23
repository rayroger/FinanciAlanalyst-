# System Architecture

## Overview

FinanciAlanalyst is a monorepo containing a Python/FastAPI backend, a Next.js frontend, shared Python packages, and Docker Compose infrastructure.

```
┌──────────────────────────────────────────────────────────────┐
│                        Browser / Client                       │
│                     Next.js 14 (TypeScript)                   │
│    Dashboard · Cashflow Chart · Category Chart · AI Cards     │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS / REST JSON
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      nginx reverse proxy                      │
│   /api/* → api:8000       /  → web:3000                      │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (Python 3.11)             │
│                                                               │
│  Routers:                                                     │
│    /api/v1/auth          JWT register + login                 │
│    /api/v1/plaid         Link token, token exchange, sync     │
│    /api/v1/transactions  List + filter transactions           │
│    /api/v1/insights      AI-generated insights                │
│                                                               │
│  Services:                                                    │
│    PlaidService     ──────────────────► Plaid API             │
│    AIService        ──────────────────► OpenAI GPT-4o         │
│    Categorizer      (rule-based, no I/O)                      │
│                                                               │
│  SQLAlchemy async ORM                                         │
└──────┬────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                    PostgreSQL 15                               │
│                                                               │
│  Tables:                                                      │
│    users          id, email, hashed_password, full_name       │
│    accounts       id, user_id (FK), plaid_item_id,            │
│                   encrypted_access_token, institution_name    │
│    transactions   id, user_id (FK), account_id (FK),          │
│                   amount, is_credit, date, category, …        │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

### Bank Connection (Plaid Link)

```
Browser                     FastAPI                 Plaid
  │                            │                      │
  │  POST /plaid/link-token     │                      │
  │ ─────────────────────────► │                      │
  │                            │  link_token_create   │
  │                            │ ────────────────────►│
  │                            │◄─────────────────────│
  │◄──────────────────────────  │  {link_token}        │
  │                            │                      │
  │  [Plaid Link SDK opens]     │                      │
  │ ────────────────────────────────────────────────► │
  │                            │        user auth      │
  │◄───────────────────────────────────────────────── │
  │  {public_token}             │                      │
  │                            │                      │
  │  POST /plaid/exchange-token │                      │
  │ ─────────────────────────► │                      │
  │                            │  item_public_token   │
  │                            │  _exchange           │
  │                            │ ────────────────────►│
  │                            │◄─────────────────────│
  │                            │  {access_token}      │
  │                            │  encrypt + store     │
  │◄──────────────────────────  │  {account_id}        │
```

### Transaction Sync

```
User → POST /plaid/sync
    → PlaidService.sync_transactions()
        → decrypt access_token (Fernet)
        → Plaid transactions/sync (paginated)
        → categorize_transaction() per txn
        → upsert into transactions table
    → return {synced: N}
```

### AI Insights

```
User → GET /insights
    → AIService.generate_insights(transactions)
        → aggregate spend by month/category
        → OpenAI GPT-4o chat completion
        → parse JSON response
        → return InsightResult
```

## Packages

| Package              | Purpose                                              |
|----------------------|------------------------------------------------------|
| `packages/core`      | Shared dataclasses (Transaction, Account, InsightResult) + categorizer |
| `packages/connectors`| Standalone Plaid API wrapper (PlaidConnector)        |
| `packages/ai`        | FinanceSummarizer (GPT-4o) + detect_anomalies()      |

## Security Architecture

See [`threat-model.md`](threat-model.md) for the full threat model.

Key controls:
- **Authentication**: bcrypt hashing + short-lived JWT (HS256)
- **Authorization**: all DB queries filter by `user_id` from JWT
- **Plaid tokens**: Fernet symmetric encryption at rest in `accounts.encrypted_access_token`
- **Secrets**: all via environment variables, never committed
- **Logging**: access tokens and PII explicitly excluded from logs
- **Transport**: HTTPS enforced by nginx in production; HTTP in local dev only
