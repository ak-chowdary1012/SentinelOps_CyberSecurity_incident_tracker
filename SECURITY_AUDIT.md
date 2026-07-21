# SentinelOps Security Audit

Audit date: 2026-07-21

## Verified controls

- Production config guardrails:
  - `ENVIRONMENT=production` without `SECRET_KEY` exits with `RuntimeError: SECRET_KEY must be set to a strong non-default value in production`.
  - `ENVIRONMENT=production` with a non-default `SECRET_KEY` and no `CORS_ORIGINS` exits with `RuntimeError: CORS_ORIGINS must be set to explicit production origins`.
  - `CORS_ORIGINS=*` exits with `RuntimeError: CORS_ORIGINS must be an explicit allowlist; wildcard origins are not allowed`.
  - With `ENVIRONMENT=production` and `CORS_ORIGINS=https://your-real-domain.example`, a request using `Origin: http://127.0.0.1:5500` returned no `access-control-allow-origin` header.
- JWT algorithm allowlist:
  - A token signed with `alg=none` returned `401`.
- Refresh tokens:
  - DB verification returned `refresh_hash_not_plain=True`.
  - Refresh rotation verification returned `refresh_rotated_old_revoked_new_active=True`.
  - Logout verification returned `logout_revoked_latest_refresh=True`.
- Auth abuse controls:
  - Ten rapid failed logins returned `[401, 401, 401, 401, 401, 429, 429, 429, 429, 429]`.
  - Weak password creation returned `422`.
- RBAC:
  - SOC Analyst forbidden mutations returned `403`.
  - Incident Manager forbidden mutations returned `403`.
  - Viewer forbidden mutations returned `403`.
- Data handling:
  - Backend raw SQL grep found no router/service raw SQL; SQL appears only in `database/schema.sql` and `database/sample_data.sql`.
  - Export formula sanitization returned `formula_export_sanitized=True`.
  - Audit redaction returned `audit_redacted=True`.
- Runtime hardening:
  - Security headers returned `X-Content-Type-Options=nosniff`, `X-Frame-Options=DENY`, and a Content Security Policy.
  - Forced unhandled exception returned `500` with `{'detail': 'Internal server error'}` and `stack_detail_leaked=False`.
- Browser login:
  - Initial Playwright run found `OPTIONS /auth/login HTTP/1.1" 400 Bad Request`; fixed by adding the local frontend origin to CORS defaults.
  - Second Playwright run logged `Failed to load resource: net::ERR_NETWORK_ACCESS_DENIED`; fixed by vendoring Chart.js `4.5.1` at `frontend/pages/vendor/chart.umd.min.js` instead of using a runtime CDN.
  - Fresh-clone browser timeout root cause: `dashboard_charts_proof.py` launched Uvicorn with `cwd=backend`, causing the default relative SQLite URL to use `backend\\cybersec_incidents.db` instead of the initialized root `cybersec_incidents.db`. The dashboard shell rendered blank canvases behind the login overlay, and the proof waited for chart pixels before proving login.
  - Fix: the proof now starts Uvicorn from the repository root with `--app-dir backend`, waits for `sentinelops_access_token` before canvas checks, reports early API subprocess exits, and writes a fallback screenshot if Windows locks the canonical proof image. Frontend login/fetch failures now log `console.error`.
  - CORS recheck: `ENVIRONMENT` was unset and `Origin: http://127.0.0.1:5500` received `access-control-allow-origin: http://127.0.0.1:5500`.
  - Final Playwright chart proof returned `browser login: ok, token present: True`, `canvas count: 5`, `canvas painted pixels: [20753, 8554, 10285, 12957, 9622]`, and `console errors: []`.
  - Screenshot reviewed at `dashboard_charts_proof_latest.png`; charts have visible rendered bars, lines, and doughnut segments.
- Dependencies:
  - Initial `pip-audit` found `ecdsa 0.19.2 PYSEC-2026-1325`.
  - After replacing `python-jose` with `PyJWT`, `pip-audit` returned `No known vulnerabilities found`.
- Container hardening:
  - `backend/Dockerfile` now creates and uses `appuser`.

## Secret review

- `.env.example`: placeholder secret only.
- `docker-compose.yml`: uses `${POSTGRES_PASSWORD:-sentinelops_dev_password_change_me}` for local development, not a production credential.
- `database/schema.sql` and `database/sample_data.sql`: no real secrets found; sample user rows contain `generated-by-application`.
- `backend/.env`: untracked ignored local file previously contained a local PostgreSQL password. It was replaced with SQLite. If that password was ever reused outside local development, rotate it.

## Blocked checks

- Real-browser proof: Playwright Chromium was installed successfully. Required dashboard chart proof returned `browser login: ok, token present: True`, `canvas count: 5`, and `console errors: []`.
- Docker Compose proof: still blocked by this Windows sandbox.
  - `winget`, `choco`, `scoop`, and `docker` are not on PATH.
  - Administrator check returned `False`.
  - `wsl --status` reported WSL is not installed.
  - Direct Docker Desktop installer download succeeded, but running it returned `The specified executable is not a valid application for this OS platform.`
  - Exact `docker compose up --build` failed with `The term 'docker' is not recognized as a name of a cmdlet, function, script file, or executable program.`
  - Must be verified by a human before production deploy with:
    `winget install --id Docker.DockerDesktop -e`
    `docker version`
    `docker info`
    `docker compose up --build -d`
    `docker compose ps`
    `docker compose exec api whoami`
    `docker compose down`
