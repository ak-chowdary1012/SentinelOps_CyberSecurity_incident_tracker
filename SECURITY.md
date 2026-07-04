# Security Policy

## Supported Version
The maintained version is the current `main` branch.

## Reporting Issues
For portfolio use, open a private advisory or contact the repository owner directly before filing a public issue for sensitive findings.

## Security Controls
- JWT access tokens.
- Refresh token hashing and revocation.
- Passlib bcrypt password hashing.
- RBAC-protected endpoints.
- Audit logging for login, logout, create, update, and delete.
- Sensitive fields excluded from serialized responses.
- Environment-based configuration through `.env`.

## Known Production Hardening Items
- Add Alembic migrations before production database evolution.
- Replace demo secrets and credentials.
- Use HTTPS-only deployment.
- Set explicit CORS origins.
- Add rate limiting and account lockout.
- Add centralized logging and monitoring.
