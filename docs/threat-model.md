# Threat Model — FinanciAlanalyst

## Scope

This document covers the threat model for the FinanciAlanalyst MVP: a web application that connects user bank accounts via Plaid, stores transaction data, and generates AI insights using OpenAI.

---

## Assets

| Asset                          | Sensitivity | Notes                                    |
|-------------------------------|-------------|------------------------------------------|
| User credentials (email + bcrypt hash) | High | Stored in `users` table |
| Plaid access tokens            | Critical    | Encrypted at rest with Fernet; never logged |
| Transaction history            | High        | PII — spending patterns, merchant names  |
| JWT access tokens              | High        | Short-lived (60 min); bearer token        |
| OpenAI API key                 | High        | Env var; if leaked, billable abuse        |
| Plaid API credentials          | High        | Env var; if leaked, data access risk      |
| Database credentials           | High        | Env var                                   |

---

## Trust Boundaries

1. **Browser ↔ nginx**: public internet — must use HTTPS in production
2. **nginx ↔ FastAPI**: internal Docker network — trusted
3. **FastAPI ↔ PostgreSQL**: internal Docker network — trusted
4. **FastAPI ↔ Plaid API**: outbound HTTPS to Plaid — verify TLS certs
5. **FastAPI ↔ OpenAI API**: outbound HTTPS to OpenAI — verify TLS certs

---

## Threats & Mitigations

### Authentication & Authorization

| Threat | Severity | Mitigation |
|--------|----------|------------|
| Brute-force login | High | Rate limiting (add slowapi in production); bcrypt cost factor |
| JWT forgery | High | Signed with HS256 + `secret_key` (min 32-byte random value) |
| JWT theft (XSS) | High | Store token in `localStorage` (current MVP); upgrade to httpOnly cookie in production |
| Horizontal privilege escalation | Critical | All DB queries include `WHERE user_id = :current_user_id` |
| Expired token reuse | Medium | Tokens expire in 60 min; no refresh token (add in v2) |

### Sensitive Data Protection

| Threat | Severity | Mitigation |
|--------|----------|------------|
| Plaid access token leakage via DB | Critical | Fernet symmetric encryption at rest in `encrypted_access_token` column |
| Plaid access token leakage via logs | Critical | Tokens explicitly NOT logged; comment in code: "SECURITY: never log access_token" |
| Bank credentials stored | Critical | Not applicable — Plaid OAuth only; we never see username/password |
| PII in logs | High | Transaction names/merchant names not logged at INFO level |
| Plaintext secrets in source code | Critical | All secrets via `.env`; `.env` in `.gitignore`; `.env.example` uses placeholders |

### API Security

| Threat | Severity | Mitigation |
|--------|----------|------------|
| CORS misconfiguration | High | Explicit `allow_origins` from env var `ALLOWED_ORIGINS` |
| SQL injection | High | SQLAlchemy ORM with parameterized queries; no raw SQL |
| Mass assignment | Medium | Pydantic schemas validate all inputs; ORM fields explicit |
| Plaid public_token replay | Medium | Exchange is one-time; Plaid invalidates after use |
| SSRF via user-controlled URLs | Low | No user-controlled URL fetching in this app |

### Infrastructure

| Threat | Severity | Mitigation |
|--------|----------|------------|
| DB credential exposure | High | `POSTGRES_PASSWORD` via env var; not default in production |
| Container privilege escalation | Medium | Run containers as non-root (add `USER` in Dockerfile for production) |
| Outdated dependencies | Medium | Pin versions in `requirements.txt`; run `pip audit` in CI |
| DoS via large transaction sync | Medium | Plaid pagination cursor; consider async background task in v2 |

### AI / Third-party

| Threat | Severity | Mitigation |
|--------|----------|------------|
| PII sent to OpenAI | High | Only aggregated spend-by-category sent, NOT raw transaction names |
| OpenAI prompt injection | Low | System prompt is server-controlled; user data is numeric only |
| OpenAI API key abuse | High | Key in env var; rotate if leaked; set spend limits on OpenAI dashboard |

---

## Recommended Production Hardening (Post-MVP)

1. **HTTPS only** — TLS termination at load balancer; HSTS header
2. **httpOnly cookies** for JWT (eliminate XSS token theft)
3. **Refresh tokens** with rotation and revocation list
4. **Rate limiting** on `/auth/token` and `/plaid/*` endpoints
5. **Key Management Service** (AWS KMS / GCP KMS) for Fernet key instead of env var
6. **Field-level encryption key rotation** procedure documented
7. **Audit logging** — who accessed what, when (separate from app logs)
8. **Plaid webhook verification** — verify `X-Plaid-Verification-Signature`
9. **Dependency scanning** — `pip audit` + `npm audit` in CI
10. **Penetration testing** before public launch
11. **Data retention policy** — purge old transactions per user request (CCPA/GDPR)
12. **Secrets manager** — Vault, AWS Secrets Manager, or equivalent

---

## Out of Scope (MVP)

- Multi-factor authentication
- SOC 2 compliance
- PCI DSS (we never handle card numbers directly)
- OAuth 2.0 social login
