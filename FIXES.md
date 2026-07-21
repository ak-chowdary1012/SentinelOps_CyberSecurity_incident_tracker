# SentinelOps Repair Log

## Phase 0 baseline

- Command: `python -m venv .venv`
  - Output: exit code 0, no stdout/stderr.
- Command: `.\\.venv\\Scripts\\python.exe -m pip install -r backend\\requirements.txt`
  - First sandboxed output: `ERROR: Could not find a version that satisfies the requirement fastapi` after `WinError 10013` socket failures.
  - Rerun with approved package-index access installed the documented dependency set, including `passlib-1.7.4` and `bcrypt-5.0.0`.
- Command: `..\\.venv\\Scripts\\python.exe init_db.py` from `backend`
  - Failure: `RuntimeError: Form data requires "python-multipart" to be installed. You can install "python-multipart" with: pip install python-multipart`.
- Command: `.\\.venv\\Scripts\\python.exe -m pytest -q`
  - Failure: collection error importing `tests/test_api.py`; same `RuntimeError: Form data requires "python-multipart" to be installed`.

## Runtime dependency and login contract

- What was wrong: `/auth/login` used `OAuth2PasswordRequestForm`, which forced form parsing while the frontend and tests sent JSON. `python-multipart` was also missing from the documented dependency set.
- Fix: `/auth/login` now accepts the existing `LoginRequest` JSON schema; `python-multipart` is present in `backend/requirements.txt`.
- Proof: pending post-fix test and smoke runs.

## Password hashing

- What was wrong: `passlib[bcrypt]` resolved to unmaintained `passlib-1.7.4` with `bcrypt-5.0.0`, the broken combination identified in the audit prompt.
- Fix: replaced Passlib usage with a small direct `bcrypt` wrapper and pinned `bcrypt==4.0.1`.
- Proof: `.\\.venv\\Scripts\\python.exe -m pytest -q` returned `4 passed, 1 warning in 2.97s`; live smoke returned `"login_token_type": "bearer"`.

## Security hardening

- What was wrong: production config could silently use a development secret, CORS could use `*`, refresh/JWT/auth abuse controls needed verification, and dependency audit found `ecdsa 0.19.2 PYSEC-2026-1325`.
- Fix: added production config failures, explicit CORS allowlist, `PyJWT`, rate limiting, username lockout, password validation, security headers, generic exception responses, export sanitization, and Docker non-root user.
- Proof:
  - `pip-audit`: `No known vulnerabilities found`.
  - Security script: `jwt_none_status: 401`, `refresh_hash_not_plain: True`, `refresh_rotated_old_revoked_new_active: True`, `logout_revoked_latest_refresh: True`, `rate_limit_statuses: [401, 401, 401, 401, 401, 429, 429, 429, 429, 429]`, `weak_password_status: 422`, all checked RBAC denials `403`, `formula_export_sanitized: True`, `audit_redacted: True`.
  - Header/error script: `x_content_type_options: nosniff`, `x_frame_options: DENY`, `content_security_policy_present: True`, `generic_500_status: 500`, `stack_detail_leaked: False`.

## Code quality

- What was wrong: Ruff found unused imports in `backend/app/models.py` and `backend/app/routers/reports.py`.
- Fix: removed the unused imports and added frontend global unhandled-rejection handling.
- Proof: `python -m ruff check backend tests` returned `All checks passed!`; `node --check frontend/pages/app.js` exited 0.

## Browser login proof defects

- What was wrong: serving `frontend/pages` from `http://127.0.0.1:5500` triggered a CORS preflight failure; API log showed `OPTIONS /auth/login HTTP/1.1" 400 Bad Request`.
- Fix: added `http://127.0.0.1:5500` and `http://localhost:5500` to the local CORS allowlist defaults and `.env.example`.
- Proof: Playwright browser login script returned `browser login: ok, token present: True`.
- What was wrong: `dashboard.html` loaded Chart.js from a CDN, which produced `console errors: ['Failed to load resource: net::ERR_NETWORK_ACCESS_DENIED']` in the sandboxed real browser.
- Fix: vendored Chart.js `4.5.1` as `frontend/pages/vendor/chart.umd.min.js`, loaded it with `<script src="vendor/chart.umd.min.js"></script>`, and kept CSP script loading scoped to `script-src 'self'`.
- Proof:
  - `rg -n "cdn|chart\\.js|Chart\\.js|chart\\.umd" frontend -S` found no external Chart.js script tag; the only CDN URL is the auditable source URL in `frontend/pages/vendor/README.md`.
  - Vendored file SHA-256: `48444A82D4EDCB5BEC0F1965FAACDDE18D9C17DB3063D042ABADA2F705C9F54A`.
  - `.\\.venv\\Scripts\\python.exe dashboard_charts_proof.py` returned:
    `browser login: ok, token present: True`
    `canvas count: 5`
    `canvas painted pixels: [31771, 9211, 36178, 27056, 35900]`
    `console errors: []`
    `screenshot: C:\\Users\\nekka\\cybersec-incident-tracker\\dashboard_charts_proof.png`
  - Screenshot reviewed: `dashboard_charts_proof.png` shows rendered severity, trend, vulnerability, health, and attack-type charts with visible lines/bars/doughnuts.

## CORS production scoping

- What was wrong: the shared default CORS allowlist included `http://127.0.0.1:5500` and `http://localhost:5500`, so production would inherit dev browser origins when `CORS_ORIGINS` was unset.
- Fix: `backend/app/config.py` now uses development defaults only when `ENVIRONMENT` is not `production`; production defaults to an empty CORS origin list and fails startup unless `CORS_ORIGINS` is set explicitly. `.env.example` labels the 5500 origins as development frontend origins.
- Proof:
  - Production with a non-default `SECRET_KEY` and no `CORS_ORIGINS` failed startup with:
    `RuntimeError: CORS_ORIGINS must be set to explicit production origins`
  - Production with `CORS_ORIGINS=https://your-real-domain.example` and request origin `http://127.0.0.1:5500` returned:
    `--- status line ---`
    `HTTP/1.1 401 Unauthorized`
    `--- access-control grep ---`
    `access-control-allow-credentials: true`
  - No `access-control-allow-origin` header was returned for `http://127.0.0.1:5500`, so the local dev origin was not reflected in production.

## Chart.js checksum self-verification

- Local command: `Get-FileHash frontend\\pages\\vendor\\chart.umd.min.js -Algorithm SHA256`
- Fresh local file hash: `48444A82D4EDCB5BEC0F1965FAACDDE18D9C17DB3063D042ABADA2F705C9F54A`
- `frontend/pages/vendor/README.md` recorded hash: `48444A82D4EDCB5BEC0F1965FAACDDE18D9C17DB3063D042ABADA2F705C9F54A`
- Fresh CDN re-fetch proof:
  - `vendored: 48444A82D4EDCB5BEC0F1965FAACDDE18D9C17DB3063D042ABADA2F705C9F54A`
  - `cdn:      48444A82D4EDCB5BEC0F1965FAACDDE18D9C17DB3063D042ABADA2F705C9F54A`
  - `diff count: 0`
- Result: the vendored file, README checksum, and pinned CDN source match exactly.

## Dashboard glass UI verification

- Fix: updated `frontend/pages/style.css` so dashboard panels/cards render as translucent frosted-glass islands over a layered gradient/grid background, with `backdrop-filter: blur(16px) saturate(150%)`, `-webkit-backdrop-filter`, light glass borders, softer elevation shadows, larger rounded corners, and brighter muted text.
- DOM stability: no dashboard IDs, canvas elements, login selectors, toast selector, or metric `data-*` attributes were changed.
- Proof: `.\\.venv\\Scripts\\python.exe dashboard_charts_proof.py` returned:
  - `browser login: ok, token present: True`
  - `canvas count: 5`
  - `canvas painted pixels: [30413, 9058, 33314, 25676, 33102]`
  - `console errors: []`
  - `screenshot: C:\\Users\\nekka\\cybersec-incident-tracker\\dashboard_charts_proof.png`
- Screenshot reviewed: cards read as translucent glass over the richer background, text is legible, and chart lines/bars/doughnut segments remain crisp.

## Docker status recheck

- `rg -n "Docker|docker|compose|human|blocked|verification" SECURITY_AUDIT.md FIXES.md CHANGELOG.md README.md SECURITY.md docs -S` confirmed `FIXES.md` and `SECURITY_AUDIT.md` still list Docker Compose proof as blocked by this Windows sandbox and requiring human verification.
- The required commands remain documented:
  - `winget install --id Docker.DockerDesktop -e`
  - `docker version`
  - `docker info`
  - `docker compose up --build -d`
  - `docker compose ps`
  - `docker compose exec api whoami`
  - `docker compose down`

## Final proof

- Fresh temp environment:
  - `python -m venv .venv`
  - `python -m pip install -r backend\\requirements.txt`
  - `python init_db.py`
  - `python -m pytest -q`
  - Output ended with `4 passed, 1 warning in 3.53s`.
- Docker proof still blocked by environment:
  - OS/package-manager detection: PowerShell reported `OS Microsoft Windows 10.0.26200`; `where.exe winget`, `where.exe choco`, `where.exe scoop`, and `where.exe docker` all returned `INFO: Could not find files for the given pattern(s).`
  - Privilege/runtime detection: administrator check returned `False`; `wsl --status` returned `The Windows Subsystem for Linux is not installed.`
  - Direct installer attempt: Docker Desktop installer downloaded to `%TEMP%\\DockerDesktopInstaller.exe` with size `334482729`, but running it returned `Program 'DockerDesktopInstaller.exe' failed to run ... The specified executable is not a valid application for this OS platform.`
  - Exact proof command: `docker compose up --build` failed with `The term 'docker' is not recognized as a name of a cmdlet, function, script file, or executable program.`
  - Must be verified by a human before production deploy:
    `winget install --id Docker.DockerDesktop -e`
    `docker version`
    `docker info`
    `docker compose up --build -d`
    `docker compose ps`
    `docker compose exec api whoami`
    `docker compose down`
- Real-browser proof completed:
  - `pip install playwright` installed `playwright-1.61.0`.
  - `playwright install --with-deps chromium` downloaded Chromium to `C:\\Users\\nekka\\AppData\\Local\\ms-playwright\\chromium-1228`.
  - Required browser script output: `browser login: ok, token present: True` and `console errors: []`.
- Full re-verification after Chart.js/CORS fix:
  - `.\\.venv\\Scripts\\python.exe -m pytest -q` returned `4 passed, 1 warning in 4.69s`.
  - `.\\.venv\\Scripts\\python.exe -m ruff check backend tests` returned `All checks passed!`.
  - `node --check frontend\\pages\\app.js` exited 0 with no output.
  - `.\\.venv\\Scripts\\pip-audit.exe -r backend\\requirements.txt` returned `No known vulnerabilities found`.
