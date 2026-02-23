"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, plaid, transactions, insights

app = FastAPI(
    title="FinanciAlanalyst API",
    version="0.1.0",
    description="AI-powered personal finance analysis",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(plaid.router, prefix="/api/v1/plaid", tags=["plaid"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["insights"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
