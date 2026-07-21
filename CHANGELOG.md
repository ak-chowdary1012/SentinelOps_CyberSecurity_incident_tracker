# Changelog

## 2.2.0 - Repair and Security Hardening
- Redesigned the SOC dashboard panels and metric cards as glassy translucent islands over a layered background while preserving the existing dashboard DOM and chart proof selectors.
- Self-verified the vendored Chart.js file checksum against `frontend/pages/vendor/README.md` and a freshly downloaded pinned CDN copy; all hashes matched `48444A82D4EDCB5BEC0F1965FAACDDE18D9C17DB3063D042ABADA2F705C9F54A`.
- Vendored Chart.js `4.5.1` locally under `frontend/pages/vendor/` and restored dashboard chart rendering without a runtime CDN dependency.
- Scoped default CORS origins to development only; production now requires explicit `CORS_ORIGINS` and does not allow the local `127.0.0.1:5500`/`localhost:5500` frontend origins by default.
- Switched `/auth/login` to the JSON `LoginRequest` contract used by the frontend and tests.
- Added `python-multipart`, replaced Passlib with direct bcrypt hashing, and moved JWT handling from `python-jose` to `PyJWT`.
- Added production startup guardrails for default `SECRET_KEY` and wildcard CORS origins.
- Added auth rate limiting, username lockout, stronger password validation, security headers, generic 500 responses, and bounded export sizes.
- Sanitized CSV/XLSX/PDF export data against spreadsheet formula injection.
- Verified hashed refresh-token storage, refresh rotation, logout revocation, server-side RBAC denials, audit redaction, dependency audit, backend lint, frontend syntax check, full tests, live API smoke, and clean venv setup.
- Docker Compose now uses an environment-supplied database password with a dev-only fallback, and the Dockerfile runs the app as a non-root user.
- Docker runtime verification remains the documented human-verification item on a host with Docker available.

## 2.1.0 - Enterprise Polish
- Added organizational risk score engine.
- Added SOC status widget metrics.
- Added incident timeline endpoint and dashboard timeline rendering.
- Added lightweight AI incident summary endpoint.
- Added users page to frontend navigation.
- Added frontend update workflows, pagination controls, skeleton loaders, empty states, and safer HTML rendering.
- Improved dashboard layout, visual polish, login screen, table interactions, and responsive states.
- Expanded API tests for RBAC, logout, dashboard risk fields, timeline, and AI summary.
- Added professional repository documentation set.
- Tightened HTTP stack dependency compatibility with `h11>=0.16`.

## 2.0.0 - Enterprise Modernization
- Refactored backend into enterprise FastAPI module structure.
- Added JWT authentication, refresh tokens, password hashing, RBAC, audit logging, dashboard metrics, exports, Docker, CI, tests, and documentation.

## 1.0.0 - Initial Academic Prototype
- Basic CRUD for systems, users, incidents, logs, vulnerabilities, and responses.
