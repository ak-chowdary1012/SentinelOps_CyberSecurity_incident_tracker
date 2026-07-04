# Contributing

## Development Setup
```bash
cd backend
python -m pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload
```

## Quality Checks
Run these before opening a pull request:
```bash
python -m pytest -q
node --check frontend/pages/app.js
```

## Pull Request Expectations
- Keep changes scoped and explain the security or SOC workflow impact.
- Add or update tests for API behavior changes.
- Update documentation for new endpoints, environment variables, or deployment steps.
- Do not commit `.env`, local databases, logs, or generated caches.

## Coding Style
- Keep route handlers thin.
- Put business logic in services.
- Use Pydantic schemas for API contracts.
- Use role dependencies for authorization decisions.
- Never expose password hashes or token hashes in responses.
