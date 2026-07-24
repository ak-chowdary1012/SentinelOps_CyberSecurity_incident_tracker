# SentinelOps™ — Cybersecurity Incident Management Platform

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-d71f00)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791)
![JWT](https://img.shields.io/badge/Auth-JWT%20%2B%20RBAC-7c3aed)
![Tests](https://img.shields.io/badge/tests-7%20passing-34d399)
![Deployment](https://img.shields.io/badge/deployment-live-success)
![License](https://img.shields.io/badge/license-MIT-blue)

**SentinelOps™** is a full-stack Security Operations Center (SOC) platform designed for incident tracking, security monitoring, vulnerability management, response coordination, auditability, and operational security analytics.

The project demonstrates production-oriented backend engineering, REST API design, database modeling, JWT authentication, role-based access control, audit logging, reporting, responsive dashboard design, containerization, automated testing, and cloud deployment.

Built and developed by **N V Avinash Krishna**.

---

## Live Deployment

### SentinelOps Web Application

**Frontend:**  
https://sentinelops-frontend-qsec.onrender.com

### Backend API

**API:**  
https://sentinelops-cybersecurity-incident.onrender.com

### Interactive API Documentation

**Swagger UI:**  
https://sentinelops-cybersecurity-incident.onrender.com/docs

**OpenAPI:**  
https://sentinelops-cybersecurity-incident.onrender.com/openapi.json

> The Render free-tier deployment may require a short startup period after inactivity.

---

## Demo Access

A SOC Analyst account is available for exploring the deployed platform.

```text
Username: analyst
Password: AnalystPass123!
```

The demo account uses the **SOC Analyst** role and therefore does not have administrative user-management permissions.

Administrative credentials are intentionally not published.

---

## Core Features

### Security Operations Dashboard

- Organizational risk score
- Threat-level monitoring
- Critical and open incident metrics
- Average resolution time
- Protected-system statistics
- Incident severity visualization
- Incident trend analytics
- SOC operational status
- Security activity views
- Responsive desktop and mobile interface

### Incident Management

- Create, view, update, search, filter, and manage security incidents
- Severity and incident-status tracking
- Incident timelines
- Response association
- Resolution tracking
- Lightweight incident summarization

### System Monitoring

- Maintain protected-system inventory
- System status monitoring
- Department classification
- Criticality tracking
- Security-event association

### Security Logs

- Centralized security-event records
- Severity classification
- Source filtering
- System association
- Search and sorting

### Vulnerability Management

- CVE tracking
- Severity classification
- Vulnerability lifecycle status
- Affected-system tracking
- Search and filtering

### Incident Response

- Response-action tracking
- Responder attribution
- Incident association
- Response-time measurement
- Response history

### Identity & Access Management

SentinelOps implements backend-enforced role-based access control.

Supported roles:

```text
Admin
SOC Analyst
Incident Manager
Viewer
```

Administrative user-management operations are restricted to the **Admin** role.

---

## Authentication & Security

SentinelOps implements:

- JWT access tokens
- Rotating refresh tokens
- Hashed refresh-token storage
- bcrypt password hashing
- OAuth2 password flow for Swagger
- Role-based authorization
- Authentication rate limiting
- Token revocation on logout
- Protected API endpoints
- Explicit production CORS allowlist
- Security response headers
- Content Security Policy
- HTTP Strict Transport Security on HTTPS
- Audit logging
- Spreadsheet-formula sanitization for exports

### Authentication Flow

```text
POST /auth/login
       │
       ▼
Access Token + Refresh Token
       │
       ▼
Authorization: Bearer <access_token>
       │
       ▼
Protected API
```

Token renewal:

```text
POST /auth/refresh
       │
       ▼
Rotated Access + Refresh Token Pair
```

Swagger OAuth2 authorization uses:

```text
POST /auth/token
```

---

## Role-Based Access Control

| Capability | Admin | SOC Analyst | Incident Manager | Viewer |
|---|:---:|:---:|:---:|:---:|
| View operational data | ✅ | ✅ | ✅ | ✅ |
| Manage incidents | ✅ | ✅ | ✅ | ❌ |
| Delete incidents | ✅ | ❌ | ✅ | ❌ |
| Manage systems | ✅ | ✅ | ✅ | ❌ |
| Delete systems | ✅ | ❌ | ❌ | ❌ |
| Manage logs | ✅ | ✅ | ❌ | ❌ |
| Delete logs | ✅ | ❌ | ❌ | ❌ |
| Manage vulnerabilities | ✅ | ✅ | ❌ | ❌ |
| Delete vulnerabilities | ✅ | ❌ | ❌ | ❌ |
| Manage responses | ✅ | ✅ | ✅ | ❌ |
| Delete responses | ✅ | ❌ | ✅ | ❌ |
| Manage users | ✅ | ❌ | ❌ | ❌ |

Authorization is enforced by the backend and is not dependent on frontend controls.

---

## Technology Stack

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- Uvicorn

### Database

- PostgreSQL-compatible SQLAlchemy schema
- SQLite for local development
- Relational models and foreign-key constraints
- Indexed operational fields

### Security

- JWT
- OAuth2
- bcrypt
- RBAC dependencies
- Refresh-token rotation
- Authentication rate limiting
- CORS allowlisting
- Security headers

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Chart.js

The production interface uses an **Obsidian, Ivory and Metallic Gold glass-style SOC design**, with responsive layouts for desktop and mobile devices.

### DevOps

- Docker
- Docker Compose
- GitHub Actions
- Render

### Testing

- Pytest
- FastAPI TestClient
- HTTPX
- Static JavaScript validation

---

## Architecture

```text
                     ┌───────────────────────┐
                     │   SentinelOps Web UI  │
                     │ HTML / CSS / JS       │
                     │ Chart.js              │
                     └───────────┬───────────┘
                                 │ HTTPS
                                 ▼
                     ┌───────────────────────┐
                     │     FastAPI API       │
                     │ Authentication / RBAC │
                     │ REST Endpoints        │
                     └───────────┬───────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
        Incident Logic       Audit Layer       Export/Analytics
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                     ┌───────────────────────┐
                     │      SQLAlchemy       │
                     │         ORM           │
                     └───────────┬───────────┘
                                 ▼
                     ┌───────────────────────┐
                     │      Database         │
                     │ PostgreSQL / SQLite   │
                     └───────────────────────┘
```

### Repository Structure

```text
frontend/pages
    Static SOC dashboard and operational workflows

backend/app
    FastAPI application

backend/app/routers
    API routes organized by business capability

backend/app/services
    Business logic, analytics, risk scoring and audit helpers

backend/app/crud
    Shared persistence operations

database
    Database schema and sample data

docs
    Architecture, API and verification documentation

tests
    Automated API and integration tests
```

Additional documentation:

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [Verification Checklist](docs/VERIFICATION_CHECKLIST.md)
- [Hiring Manager Review](docs/HIRING_MANAGER_REVIEW.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

---

## Data Model

```text
users
  │
  ├────< refresh_tokens
  │
  └────< audit_logs

systems
  │
  └────< logs

incidents
  │
  └────< responses
```

Audit records capture information including:

```text
user
action
entity
entity_id
before_value
after_value
ip_address
timestamp
```

---

## API Capabilities

Major API groups include:

```text
/auth
/users
/incidents
/systems
/logs
/vulnerabilities
/responses
```

The deployed Swagger interface provides interactive documentation and authenticated endpoint testing.

---

## Reporting & Export

Operational records can be exported in:

- CSV
- Microsoft Excel (XLSX)
- PDF

Export generation includes spreadsheet-formula sanitization to reduce formula-injection risk.

---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/ak-chowdary1012/SentinelOps_CyberSecurity_incident_tracker.git
cd SentinelOps_CyberSecurity_incident_tracker
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Install backend dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### 4. Initialize the database

```powershell
.\.venv\Scripts\python.exe backend\init_db.py
```

### 5. Start the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

### 6. Start the frontend

In another terminal:

```powershell
python -m http.server 5500 --directory frontend\pages
```

Open:

```text
Frontend:
http://127.0.0.1:5500/dashboard.html

Swagger:
http://127.0.0.1:8000/docs
```

---

## Docker

```bash
docker compose up --build
```

The backend API will be available locally at:

```text
http://127.0.0.1:8000
```

---

## Production Deployment

SentinelOps is currently deployed on **Render** as two services:

```text
Static Frontend
       │
       │ HTTPS / CORS
       ▼
FastAPI Backend
       │
       ▼
Database
```

The frontend automatically selects:

```text
http://127.0.0.1:8000
```

during local development and the production Render API when deployed.

Production CORS uses an explicit frontend-origin allowlist.

---

## Testing

Run the complete automated test suite:

```bash
python -m pytest
```

Current verified result:

```text
7 passed
```

Validate frontend JavaScript:

```bash
node --check frontend/pages/app.js
```

Additional project verification includes:

```bash
python -m ruff check backend tests
python -m pip_audit -r backend/requirements.txt
```

Verified security/lint results:

```text
No known vulnerabilities found
All checks passed!
```

---

## Engineering Highlights

SentinelOps demonstrates practical implementation of:

- RESTful API architecture
- Secure authentication
- OAuth2 integration
- JWT lifecycle management
- Backend-enforced RBAC
- Relational database modeling
- Auditability
- Secure export generation
- SOC-oriented analytics
- Responsive frontend engineering
- Dockerized deployment
- Production CORS configuration
- Automated API testing
- Cloud deployment

---

## Future Enhancements

Planned extensions include:

- Alembic database migrations
- Playwright end-to-end browser tests
- OpenTelemetry tracing
- Structured observability and metrics
- SIEM ingestion adapters
- Alert correlation
- Analyst assignment workflows
- Enhanced incident intelligence
- Additional SOC automation

---

## Repository Standards

- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Release Notes](docs/RELEASE_NOTES.md)

---

## Author

**N V Avinash Krishna**

Cybersecurity • Software Engineering • Security Operations

SentinelOps™ was designed and developed as a full-stack cybersecurity engineering project demonstrating secure application architecture, SOC workflows, backend engineering, RBAC, auditability, analytics, and production deployment.

---

## License

This project is licensed under the MIT License.

© 2026 N V Avinash Krishna