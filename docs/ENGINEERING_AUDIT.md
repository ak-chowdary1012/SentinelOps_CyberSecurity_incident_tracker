# Engineering Audit Report

## Critical Issues Found
- Hard-coded PostgreSQL credentials were embedded in application code.
- The API had no authentication, authorization, password hashing, refresh tokens, or RBAC.
- Write operations did not generate audit records.
- Raw SQLAlchemy integrity errors could surface as 500 responses.
- Frontend success alerts fired even when requests failed.
- `datetime-local` frontend values did not match backend timestamp parsing.
- The backend was a single file mixing models, schemas, database setup, and route logic.

## Major Issues Found
- Only list/create workflows existed; update/delete were missing.
- No global search, filtering, sorting, pagination, or reporting existed.
- Foreign key validation was incomplete.
- CORS allowed all origins with credentials.
- No automated tests, CI, Dockerfile, compose stack, or environment template existed.
- Database initialization imported the wrong module path.
- Pydantic models used ad hoc string dates instead of typed datetimes.
- The dashboard was a CRUD menu, not an SOC operational dashboard.

## Minor Issues Found
- Duplicate CSS existed in two frontend folders.
- Manual ID inputs were displayed but ignored by the API.
- UI layout looked like a student assignment rather than a security platform.
- README and repository metadata were missing or incomplete.

## Code Smells And Technical Debt
- Business logic inside route handlers.
- No reusable CRUD/service patterns.
- Weak naming consistency across entities.
- No centralized settings or dependency injection.
- No test isolation strategy beyond seeded demo data.

## Security Risks
- Credential leakage through source code.
- No endpoint protection.
- No role boundaries.
- No immutable audit history.
- No refresh-token revocation.
- No explicit sensitive-field exclusion from serialized user output.

## Architecture Problems
- Backend modules were not separated by concern.
- Frontend/backend contracts were implicit and brittle.
- No deployment architecture or environment-based configuration.
- No database schema documentation.

## Performance Problems
- No useful indexes for incident status/severity, log timestamps, or audit queries.
- No pagination support on list endpoints.
- Dashboard aggregations are acceptable for portfolio/demo scale but should move to materialized views or cached rollups for high-volume SOC telemetry.

## Remediation Completed
- Refactored backend into `config`, `database`, `models`, `schemas`, `crud`, `services`, `security`, `dependencies`, and routers.
- Added JWT auth, hashed passwords, refresh tokens, RBAC, and protected endpoints.
- Added immutable audit logging for create/update/delete/login/logout.
- Added full CRUD, filtering, sorting, pagination parameters, global search, dashboard metrics, and CSV/XLSX/PDF exports.
- Rebuilt frontend into a dark SOC dashboard with Chart.js visualizations and authenticated workflows.
- Added schema SQL, sample data, tests, Docker, Compose, CI, `.env.example`, `.gitignore`, license, and professional documentation.
- Added organizational risk scoring, SOC status widgets, incident timeline, and lightweight AI incident summary.
- Added frontend users workflow, update mode, pagination controls, skeleton loaders, empty states, safer HTML rendering, and improved dashboard UI.
- Fixed refresh token datetime comparison across SQLite/PostgreSQL behavior.
- Tightened dependency compatibility with `h11>=0.16`.
