# Deployment Guide

## Backend On Render
1. Create a new Web Service from the repository.
2. Set root directory to `backend`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example`.
6. Set `DATABASE_URL` to a managed PostgreSQL connection string.

## Backend On Railway
1. Create a Railway project.
2. Add a PostgreSQL service.
3. Deploy the repository service using `backend` as the root.
4. Set `DATABASE_URL` from Railway PostgreSQL.
5. Set `SECRET_KEY` and `CORS_ORIGINS`.

## Docker
```bash
docker compose up --build
```

## Frontend On Netlify
1. Deploy `frontend/pages` as a static site.
2. If backend is remote, define `window.API_BASE` before loading `app.js` or add a small environment-specific config script.
3. Set backend `CORS_ORIGINS` to the Netlify domain.

## Frontend On Vercel
1. Import the repository.
2. Use `frontend/pages` as the output/static directory.
3. Configure API base URL as described above.

## Database Providers
- Neon: use the pooled or direct PostgreSQL connection string as `DATABASE_URL`.
- Railway PostgreSQL: use the generated internal URL for Railway-hosted API.
- Supabase: use the PostgreSQL connection string and ensure SSL requirements are met.

## Production Checklist
- Replace demo credentials and secret key.
- Disable permissive CORS.
- Use HTTPS.
- Run tests in CI.
- Configure database backups.
- Add migrations before schema changes.
