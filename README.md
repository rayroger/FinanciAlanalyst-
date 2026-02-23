# FinanciAlanalyst

> AI-powered personal finance analysis — connect your bank via Plaid, get GPT-4o insights on your spending.

## Overview

FinanciAlanalyst is a full-stack MVP that lets users securely connect their bank accounts through [Plaid](https://plaid.com), automatically categorize transactions, and receive AI-generated financial insights powered by OpenAI GPT-4o.

```
┌─────────────┐     Plaid API      ┌──────────────┐
│  Next.js 14 │ ◄─── Plaid Link ──► │  FastAPI     │
│  Dashboard  │ ◄── REST/JSON  ──► │  Backend     │
└─────────────┘                    └──────┬───────┘
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                         PostgreSQL   OpenAI      Plaid API
                                      GPT-4o
```

## Tech Stack

| Layer       | Technology                                              |
|-------------|---------------------------------------------------------|
| Frontend    | Next.js 14, TypeScript, Tailwind CSS, Recharts          |
| Backend     | Python 3.11, FastAPI, SQLAlchemy async                  |
| Database    | PostgreSQL 15                                           |
| Auth        | JWT (python-jose) + bcrypt                              |
| Bank Link   | Plaid API (Link SDK)                                    |
| AI          | OpenAI GPT-4o                                           |
| Infra       | Docker Compose, nginx reverse proxy                     |

## Quick Start

### Prerequisites

- Docker & Docker Compose v2
- Plaid developer account (free sandbox): https://dashboard.plaid.com
- OpenAI API key: https://platform.openai.com

### 1. Clone & configure

```bash
git clone https://github.com/your-org/FinanciAlanalyst.git
cd FinanciAlanalyst

# Backend environment
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env with your credentials

# Frontend environment
cp apps/web/.env.example apps/web/.env.local
# Edit apps/web/.env.local with your API URL
```

### 2. Start services

```bash
docker compose up --build
```

Services:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

## Project Structure

```
FinanciAlanalyst/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js 14 frontend
├── packages/
│   ├── core/         # Shared Python types & categorization
│   ├── connectors/   # Plaid API wrapper
│   └── ai/           # AI summarization & anomaly detection
├── infra/            # Docker Compose + nginx config
└── docs/             # Architecture & threat model
```

## API Endpoints

| Method | Path                           | Description                     |
|--------|--------------------------------|---------------------------------|
| POST   | `/api/v1/auth/register`        | Register a new user             |
| POST   | `/api/v1/auth/token`           | Login → JWT access token        |
| POST   | `/api/v1/plaid/link-token`     | Create Plaid Link token         |
| POST   | `/api/v1/plaid/exchange-token` | Exchange public_token           |
| POST   | `/api/v1/plaid/sync`           | Sync latest transactions        |
| GET    | `/api/v1/transactions`         | List transactions (filterable)  |
| GET    | `/api/v1/insights`             | AI-generated financial insights |

## Security

- **No stored credentials** — bank access is OAuth-only via Plaid
- **JWT authentication** — short-lived access tokens
- **Secrets via env vars** — never hardcoded
- **Field-level encryption** — Plaid access tokens encrypted at rest (Fernet)
- **Per-user isolation** — all DB queries scoped by `user_id`
- See [`docs/threat-model.md`](docs/threat-model.md) for full threat model

## Development

### Backend only

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend only

```bash
cd apps/web
npm install
npm run dev
```

### Running tests

```bash
cd apps/api
pytest tests/ -v
```

## Environment Variables

### Backend (`apps/api/.env`)

| Variable          | Description                              |
|-------------------|------------------------------------------|
| `DATABASE_URL`    | PostgreSQL async URL                     |
| `SECRET_KEY`      | JWT signing secret (min 32 chars)        |
| `PLAID_CLIENT_ID` | Plaid client ID                          |
| `PLAID_SECRET`    | Plaid secret key                         |
| `PLAID_ENV`       | `sandbox` / `development` / `production` |
| `OPENAI_API_KEY`  | OpenAI API key                           |
| `ENCRYPTION_KEY`  | Fernet key for token encryption          |

### Frontend (`apps/web/.env.local`)

| Variable              | Description              |
|-----------------------|--------------------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL     |

## License

MIT 
