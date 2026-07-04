# Project Structure

```text
.
├── backend/
│   ├── Dockerfile
│   ├── init_db.py
│   ├── requirements.txt
│   └── app/
│       ├── config.py
│       ├── crud.py
│       ├── database.py
│       ├── dependencies.py
│       ├── main.py
│       ├── models.py
│       ├── schemas.py
│       ├── security.py
│       ├── services.py
│       └── routers/
├── database/
│   ├── schema.sql
│   └── sample_data.sql
├── docs/
├── frontend/
│   ├── css/
│   └── pages/
├── tests/
├── docker-compose.yml
├── README.md
└── .github/workflows/ci.yml
```

## Design Intent
- `routers/`: HTTP boundary and dependency wiring.
- `schemas.py`: public API contracts.
- `models.py`: database persistence model.
- `services.py`: risk scoring, audit helpers, dashboard aggregation, AI summary, and export helpers.
- `crud.py`: shared persistence behavior, pagination, sorting, filtering, and conflict handling.
