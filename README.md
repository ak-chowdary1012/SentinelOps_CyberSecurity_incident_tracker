# SentinelOps Cybersecurity Incident Platform

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-d71f00)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791)
![JWT](https://img.shields.io/badge/Auth-JWT%20%2B%20RBAC-7c3aed)
![Tests](https://img.shields.io/badge/tests-4%20passing%20verified-34d399)
![License](https://img.shields.io/badge/license-MIT-blue)

SentinelOps is an enterprise-style Security Operations Center platform for tracking incidents, security events, systems, vulnerabilities, responses, users, and audit activity. It is designed as a realistic portfolio project that demonstrates backend architecture, REST API design, database modeling, authentication, RBAC, auditability, reporting, and SOC dashboard UX.

The project intentionally keeps the stack approachable while presenting production-oriented engineering practices: FastAPI, SQLAlchemy, PostgreSQL-compatible schema design, JWT authentication, refresh tokens, password hashing, immutable audit logs, Docker, CI, tests, and a dark SOC dashboard.

## Core Features
- JWT authentication, hashed/rotated refresh tokens, logout, bcrypt password hashing, rate-limited auth, and role-based access control.
- Roles: Admin, SOC Analyst, Incident Manager, Viewer.
- CRUD workflows for users, systems, incidents, logs, vulnerabilities, and responses.
- Immutable audit logging for create, update, delete, login, and logout events.
- SOC command dashboard with KPIs, risk score, threat level, alert count, analysts online, systems protected, trend charts, timeline, and activity feed.
- Incident timeline for Created, Assigned, Investigated, Resolved, and Closed stages.
- Lightweight AI incident summary and severity/category recommendation endpoint.
- Global search, entity filters, sorting, bounded pagination parameters, CSV/XLSX/PDF exports with spreadsheet-formula sanitization.
- Docker, Docker Compose, GitHub Actions CI, `.env.example`, schema SQL, sample data, and automated API tests.

## Technology Stack
- Backend: FastAPI, Pydantic, SQLAlchemy 2.0
- Database: PostgreSQL-ready schema, SQLite default for local demo
- Security: JWT, hashed refresh tokens, direct bcrypt hashing, RBAC dependencies, auth rate limiting
- Frontend: HTML, CSS, JavaScript, Chart.js
- DevOps: Docker, Docker Compose, GitHub Actions
- Testing: Pytest, FastAPI TestClient, HTTPX

## Architecture
```text
frontend/pages      Static SOC dashboard and workflows
backend/app         FastAPI application
backend/app/routers Route modules by business capability
backend/app/services Business logic, risk scoring, audit helpers
backend/app/crud    Shared persistence operations
database            PostgreSQL schema and sample data
docs                Architecture, API, verification, screenshots
tests               Integration/API tests
```

More detail:
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [Verification Checklist](docs/VERIFICATION_CHECKLIST.md)
- [Hiring Manager Review](docs/HIRING_MANAGER_REVIEW.md)

## ER Diagram
```text
users 1---* refresh_tokens
users 1---* audit_logs
systems 1---* logs
incidents 1---* responses
audit_logs records user/action/entity/before/after/ip/timestamp
```

## Authentication Flow
```text
POST /auth/login -> access token + refresh token
Authorization: Bearer <access_token> -> protected API access
POST /auth/refresh -> rotated access/refresh pair
POST /auth/logout -> refresh token revoked + audit event
```

## Quick Start
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\init_db.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

In a second shell, serve the frontend:
```powershell
python -m http.server 5500 --directory frontend\pages
```

Open:
- API docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:5500/dashboard.html`

Demo users:
```text
admin / AdminPass123!
analyst / AnalystPass123!
```

## Docker
```bash
docker compose up --build
```

The API runs at `http://127.0.0.1:8000`.

## Deployment
Backend targets:
- Render
- Railway
- Docker-compatible hosts

Frontend targets:
- Netlify
- Vercel
- Static file hosting

Database targets:
- Neon
- Railway PostgreSQL
- Supabase PostgreSQL

See [Deployment Guide](docs/DEPLOYMENT.md).

## Screenshots
The repository includes a professional screenshot checklist covering dashboard, login, CRUD pages, charts, Swagger, architecture, ER diagram, mobile view, and dark theme.

See [Screenshot Checklist](docs/SCREENSHOT_CHECKLIST.md).

## Testing
```bash
python -m pytest -q
```

Current verified result:
```text
4 passed, 1 warning in 2.98s
```

Additional static frontend check:
```bash
node --check frontend/pages/app.js
```

Live API smoke from a running local API:
```powershell
.\.venv\Scripts\python.exe live_api_smoke.py
```

Browser dashboard proof:
```powershell
.\.venv\Scripts\python.exe dashboard_charts_proof.py
```

Security checks run during the latest audit:
```bash
python -m pip_audit -r backend/requirements.txt
python -m ruff check backend tests
```

Current verified security/lint results:
```text
No known vulnerabilities found
All checks passed!
```

## Future Enhancements
- Alembic migrations.
- Playwright browser tests and screenshot automation.
- OpenTelemetry traces, structured logs, and metrics.
- SIEM ingestion adapters.
- Alert correlation and analyst assignment workflow.
- Hosted demo environment and real screenshots in `docs/screenshots/`.

## Repository Standards
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Release Notes](docs/RELEASE_NOTES.md)

## Fresh Clone Verified

Verified on 2026-07-21 from a separate clone directory with no copied local database, virtualenv, proof image, or `.env` from the working checkout:

```powershell
git clone C:\Users\nekka\cybersec-incident-tracker sentinelops-freshclone
cd sentinelops-freshclone
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\init_db.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
.\.venv\Scripts\python.exe live_api_smoke.py
.\.venv\Scripts\python.exe dashboard_charts_proof.py
```

The browser proof generates `dashboard_charts_proof.png` locally; the image is ignored by Git.

## License
MIT
