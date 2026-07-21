from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect


from app.config import get_settings
from app.database import SessionLocal, engine
from app.models import (
    Base,
    AuditLog,
    Incident,
    IncidentStatus,
    Log,
    Role,
    Severity,
    System,
    SystemStatus,
    User,
    Vulnerability,
    VulnerabilityStatus,
)
from app.routers import ROUTERS
from app.security import hash_password
from app.services import write_audit


settings = get_settings()
logger = logging.getLogger("sentinelops")

BASE_CSP = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "img-src 'self' data:; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "connect-src 'self'; "
    "form-action 'self'"
)
DOCS_CSP = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "connect-src 'self'; "
    "form-action 'self'"
)
DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Create all database tables
        Base.metadata.create_all(bind=engine)

        # Seed demo data only if enabled
        if settings.seed_demo_data:
            seed_demo_data()

        app.state.db_ready = database_schema_ready()

        if app.state.db_ready:
            logger.info("Database initialized successfully.")
        else:
            logger.error("Database schema verification failed after initialization.")

    except Exception:
        logger.exception("Database initialization failed")
        app.state.db_ready = False

    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="2.0.0",
        description="Enterprise-style Security Operations Center incident tracking platform.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for router in ROUTERS:
        app.include_router(router)

    @app.middleware("http")
    async def require_initialized_database(request: Request, call_next):
        ALLOWED_WHEN_DB_NOT_READY = (
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        )

        if (
            not request.url.path.startswith(ALLOWED_WHEN_DB_NOT_READY)
            and not database_schema_ready()
        ):
            return JSONResponse(
                status_code=503,
                content={"detail": database_not_ready_message()},
            )

        return await call_next(request)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        if request.url.path.startswith(DOCS_PATHS):
            response.headers["Content-Security-Policy"] = DOCS_CSP
        else:
            response.headers["Content-Security-Policy"] = BASE_CSP
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception for %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.get("/health", tags=["Health"])
    def health() -> dict[str, str]:
        if not database_schema_ready():
            return {"status": "setup_required", "service": settings.app_name, "detail": database_not_ready_message()}
        return {"status": "ok", "service": settings.app_name}

    return app


def database_not_ready_message() -> str:
    return "Database initialization failed."


def database_schema_ready() -> bool:
    try:
        inspector = inspect(engine)
        return all(inspector.has_table(table) for table in ("users", "incidents", "audit_logs"))
    except Exception:
        logger.exception("Database readiness check failed")
        return False


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == "admin").first():
            return

        admin = User(
            username="admin",
            name="SOC Administrator",
            role=Role.admin,
            contact="soc-admin@example.com",
            hashed_password=hash_password("AdminPass123!"),
        )
        analyst = User(
            username="analyst",
            name="Maya Rao",
            role=Role.soc_analyst,
            contact="maya.rao@example.com",
            hashed_password=hash_password("AnalystPass123!"),
        )
        db.add_all([admin, analyst])
        db.flush()

        systems = [
            System(
                name="Identity Provider",
                ip_address="10.40.1.10",
                department="Security",
                status=SystemStatus.online,
                criticality=Severity.critical,
            ),
            System(
                name="Payment API",
                ip_address="10.20.3.15",
                department="Finance",
                status=SystemStatus.degraded,
                criticality=Severity.high,
            ),
            System(
                name="Endpoint Fleet",
                ip_address="10.70.0.21",
                department="IT",
                status=SystemStatus.online,
                criticality=Severity.medium,
            ),
        ]
        db.add_all(systems)
        db.flush()

        now = datetime.now(timezone.utc)
        incidents = [
            Incident(
                date=now - timedelta(days=6),
                type="Malware",
                severity=Severity.critical,
                status=IncidentStatus.investigating,
                description="Endpoint beaconing detected from finance subnet.",
            ),
            Incident(
                date=now - timedelta(days=4),
                type="Phishing",
                severity=Severity.high,
                status=IncidentStatus.contained,
                description="Credential harvesting campaign targeting executives.",
            ),
            Incident(
                date=now - timedelta(days=2),
                type="Unauthorized Access",
                severity=Severity.medium,
                status=IncidentStatus.resolved,
                description="Suspicious admin login blocked.",
                resolved_at=now - timedelta(days=1, hours=20),
            ),
        ]
        db.add_all(incidents)
        db.flush()

        db.add_all(
            [
                Log(
                    timestamp=now - timedelta(hours=5),
                    event="Multiple failed MFA challenges",
                    source="identity",
                    severity=Severity.high,
                    system_id=systems[0].system_id,
                ),
                Log(
                    timestamp=now - timedelta(hours=3),
                    event="EDR isolated host FIN-022",
                    source="edr",
                    severity=Severity.critical,
                    system_id=systems[1].system_id,
                ),
                Log(
                    timestamp=now - timedelta(hours=1),
                    event="Firewall blocked outbound C2 traffic",
                    source="firewall",
                    severity=Severity.high,
                    system_id=systems[2].system_id,
                ),
                Vulnerability(
                    description="Outdated OpenSSL package on payment gateway",
                    severity=Severity.high,
                    status=VulnerabilityStatus.in_progress,
                    cve="CVE-2023-0286",
                    affected_system="Payment API",
                ),
                Vulnerability(
                    description="Critical identity provider patch pending",
                    severity=Severity.critical,
                    status=VulnerabilityStatus.open,
                    cve="CVE-2024-3094",
                    affected_system="Identity Provider",
                ),
            ]
        )
        write_audit(db, user=admin, action="CREATE", entity="seed", after={"records": "demo dataset"})
        db.commit()
    finally:
        db.close()


app = create_app()
