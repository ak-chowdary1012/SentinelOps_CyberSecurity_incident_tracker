# Verification Checklist

## Backend
- [x] Application imports successfully.
- [x] Live `uvicorn` health check returns `ok`.
- [x] Database schema initializes.
- [x] Demo data seeds successfully.
- [x] `/health` returns 200.
- [x] Protected endpoints reject anonymous requests.
- [x] Login returns access and refresh tokens.
- [x] Refresh token rotation works.
- [x] Logout revokes refresh token and writes audit event.
- [x] RBAC denies restricted admin endpoints for analyst role.
- [x] Current user endpoint excludes password hashes.
- [x] Systems CRUD creates, updates, lists, and deletes records.
- [x] Incidents CRUD creates, updates, lists, and deletes records.
- [x] Incident timeline endpoint returns Created, Assigned, Investigated, Resolved, and Closed stages.
- [x] AI incident summary endpoint returns category, severity recommendation, rationale, and next actions.
- [x] Logs validate system relationships.
- [x] Logs CRUD creates, updates, lists, and deletes records.
- [x] Vulnerabilities CRUD creates, updates, lists, and deletes records.
- [x] Responses validate incident relationships.
- [x] Responses CRUD creates, updates, lists, and deletes records.
- [x] Audit logs are generated for writes and auth events.
- [x] Dashboard metrics return KPI, risk score, SOC status, timeline, and chart data.
- [x] Global search returns grouped entity matches.
- [x] CSV export returns `text/csv`.
- [x] XLSX export returns a valid ZIP-based workbook.
- [x] PDF export returns a valid PDF header.
- [x] Duplicate unique records return conflict behavior instead of raw 500s.

## Frontend
- [x] Existing URLs remain available.
- [x] Static frontend pages return HTTP 200 for dashboard, incidents, systems, logs, vulnerabilities, responses, and users.
- [x] Login overlay stores bearer token.
- [x] Requests include Authorization headers.
- [x] Success notifications are only shown after successful API responses.
- [x] ISO datetime values are sent to the backend.
- [x] Entity tables support search, sort, filters, refresh, update, delete, pagination, and export where supported.
- [x] Dashboard includes KPI cards, threat level, risk score, SOC status, charts, timeline, recent events, and audit activity.
- [x] Users page is available in navigation.
- [x] Loading skeletons and empty states are implemented.
- [x] Toast notifications are implemented.
- [x] JavaScript syntax validates with `node --check`.

## Deployment
- [x] Dockerfile added for API.
- [x] Docker Compose added with PostgreSQL and API services.
- [x] `.env.example` added.
- [x] GitHub Actions CI added.
- [x] PostgreSQL schema and sample data scripts added.
- [x] Changelog, contributing guide, security policy, code of conduct, architecture docs, API reference, deployment guide, and screenshot checklist added.

## Verification Command
```bash
python -m pytest -q
python -W error::DeprecationWarning -m pytest -q
node --check frontend/pages/app.js
```

Last local result: `4 passed`.

Live checks:
```text
GET /health -> ok
dashboard.html -> 200
index.html -> 200
systems.html -> 200
logs.html -> 200
vulnerabilities.html -> 200
responses.html -> 200
users.html -> 200
```

## Browser Automation Note
Playwright is not installed locally and `npx playwright --version` timed out in the restricted network environment. Manual browser verification and screenshot capture steps are listed in `docs/SCREENSHOT_CHECKLIST.md`.
