# SentinelOps Cybersecurity Incident Platform

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-d71f00)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791)
![JWT](https://img.shields.io/badge/Auth-JWT%20%2B%20RBAC-7c3aed)
![Tests](https://img.shields.io/badge/tests-4%20passing-34d399)
![License](https://img.shields.io/badge/license-MIT-blue)

SentinelOps is an enterprise-style Security Operations Center platform for tracking incidents, security events, systems, vulnerabilities, responses, users, and audit activity. It is designed as a realistic portfolio project that demonstrates backend architecture, REST API design, database modeling, authentication, RBAC, auditability, reporting, and SOC dashboard UX.

The project intentionally keeps the stack approachable while presenting production-oriented engineering practices: FastAPI, SQLAlchemy, PostgreSQL-compatible schema design, JWT authentication, refresh tokens, password hashing, immutable audit logs, Docker, CI, tests, and a dark SOC dashboard with Chart.js visualizations.

## Core Features
- JWT authentication, refresh tokens, logout, password hashing, and role-based access control.
- Roles: Admin, SOC Analyst, Incident Manager, Viewer.
- CRUD workflows for users, systems, incidents, logs, vulnerabilities, and responses.
- Immutable audit logging for create, update, delete, login, and logout events.
- SOC command dashboard with KPIs, risk score, threat level, alert count, analysts online, systems protected, trend charts, timeline, and activity feed.
- Incident timeline for Created, Assigned, Investigated, Resolved, and Closed stages.
- Lightweight AI incident summary and severity/category recommendation endpoint.
- Global search, entity filters, sorting, pagination parameters, CSV/XLSX/PDF exports.
- Docker, Docker Compose, GitHub Actions CI, `.env.example`, schema SQL, sample data, and automated API tests.

## Technology Stack
- Backend: FastAPI, Pydantic, SQLAlchemy 2.0
- Database: PostgreSQL-ready schema, SQLite default for local demo
- Security: JWT, refresh tokens, Passlib bcrypt hashing, RBAC dependencies
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
```bash
cd backend
python -m pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload
```

Open:
- API docs: `http://127.0.0.1:8000/docs`
- Frontend: `frontend/pages/dashboard.html`

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
4 passed
```

Additional static frontend check:
```bash
node --check frontend/pages/app.js
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

## License
MIT
