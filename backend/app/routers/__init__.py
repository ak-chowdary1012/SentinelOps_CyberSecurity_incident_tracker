from app.routers import audit, auth, dashboard, incidents, logs, reports, responses, search, systems, users, vulnerabilities


ROUTERS = [
    auth.router,
    users.router,
    systems.router,
    incidents.router,
    logs.router,
    vulnerabilities.router,
    responses.router,
    audit.router,
    dashboard.router,
    search.router,
    reports.router,
]
