# Architecture

## System Overview
SentinelOps is organized as a small but realistic SOC platform with a static frontend, FastAPI backend, and relational database.

```text
Browser
  |
  | HTML/CSS/JavaScript + Chart.js
  v
FastAPI API
  |
  | routers -> dependencies -> services -> crud
  v
SQLAlchemy ORM
  |
  v
PostgreSQL / SQLite local demo
```

## Backend Layers
- API routers validate auth and expose domain endpoints.
- Dependencies enforce JWT authentication and RBAC.
- Schemas define request and response contracts.
- Services contain business behavior: audit logging, risk scoring, dashboard metrics, token issuing, export helpers, and AI summary logic.
- CRUD centralizes query, pagination, filtering, sorting, update, delete, and conflict handling.
- Models define persistence, relationships, indexes, and constraints.

## Security Architecture
```text
User credentials -> bcrypt verification
Login -> access JWT + hashed refresh token
Protected request -> OAuth2 bearer dependency -> active user lookup
Role dependency -> endpoint authorization
Mutation/auth event -> immutable audit log
```

## Data Model
```text
User
  ├── RefreshToken
  └── AuditLog
System
  └── Log
Incident
  └── Response
Vulnerability
```

## Enterprise Readiness Notes
The project is production-oriented but intentionally lightweight. Before real production use, add Alembic migrations, external secret management, rate limiting, observability, and hosted browser test automation.
