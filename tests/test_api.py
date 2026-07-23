from fastapi.testclient import TestClient
from uuid import uuid4

import app.main as main_module
from app.database import Base, engine
from app.main import app
from app.main import seed_demo_data


Base.metadata.create_all(bind=engine)
seed_demo_data()


client = TestClient(app)


def test_public_utility_endpoints_and_csp():
    root = client.get("/")
    assert root.status_code == 200
    assert root.json() == {
        "name": "SentinelOps Cybersecurity Incident Platform",
        "version": "2.0.0",
        "status": "online",
        "health": "/health",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }

    docs = client.get("/docs")
    assert docs.status_code == 200
    docs_csp = docs.headers["content-security-policy"]
    assert "https://cdn.jsdelivr.net" in docs_csp
    assert "*" not in docs_csp

    redoc = client.get("/redoc")
    assert redoc.status_code == 200
    assert "https://cdn.jsdelivr.net" in redoc.headers["content-security-policy"]

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "SentinelOps Cybersecurity Incident Platform"

    protected = client.get("/incidents")
    assert protected.status_code == 401
    protected_csp = protected.headers["content-security-policy"]
    assert "https://cdn.jsdelivr.net" not in protected_csp
    assert "*" not in protected_csp


def test_database_readiness_middleware_allows_only_public_utility_paths(monkeypatch):
    monkeypatch.setattr(main_module, "database_schema_ready", lambda: False)

    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert client.get("/openapi.json").status_code == 200

    protected = client.get("/incidents")
    assert protected.status_code == 503
    assert protected.json() == {"detail": "Database initialization failed."}


def unique_ip() -> str:
    token = uuid4().int
    return f"10.{(token >> 16) % 200 + 20}.{(token >> 8) % 250}.{token % 250 + 1}"


def auth_headers() -> dict[str, str]:
    response = client.post("/auth/login", json={"username": "admin", "password": "AdminPass123!"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def analyst_headers() -> dict[str, str]:
    response = client.post("/auth/login", json={"username": "analyst", "password": "AnalystPass123!"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_and_authentication():
    assert client.get("/health").status_code == 200
    assert client.get("/incidents").status_code == 401
    headers = auth_headers()
    assert client.get("/users/me", headers=headers).status_code == 200

    login = client.post("/auth/login", json={"username": "admin", "password": "AdminPass123!"})
    refresh = client.post("/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    assert refresh.status_code == 200


def test_core_crud_and_audit_flow():
    headers = auth_headers()

    system_payload = {
        "name": "Test SIEM Collector",
        "ip_address": unique_ip(),
        "department": "Security",
        "status": "Online",
        "criticality": "High",
    }
    system = client.post("/systems", headers=headers, json=system_payload)
    assert system.status_code == 201
    system_id = system.json()["system_id"]
    updated_system = client.put(
        f"/systems/{system_id}",
        headers=headers,
        json={**system_payload, "status": "Degraded"},
    )
    assert updated_system.status_code == 200
    systems = client.get("/systems?search=SIEM", headers=headers)
    assert systems.status_code == 200

    incident = client.post(
        "/incidents",
        headers=headers,
        json={
            "date": "2026-07-04T10:00:00Z",
            "type": "Credential Theft",
            "severity": "High",
            "status": "Open",
            "description": "Suspicious identity activity in test flow.",
        },
    )
    assert incident.status_code == 201
    incident_id = incident.json()["incident_id"]
    updated_incident = client.put(
        f"/incidents/{incident_id}",
        headers=headers,
        json={
            "status": "Investigating",
            "severity": "High",
            "type": "Credential Theft",
            "description": "Updated investigation narrative.",
        },
    )
    assert updated_incident.status_code == 200

    log = client.post(
        "/logs",
        headers=headers,
        json={
            "timestamp": "2026-07-04T10:03:00Z",
            "event": "Impossible travel alert",
            "source": "identity",
            "severity": "High",
        },
    )
    assert log.status_code == 201
    log_id = log.json()["log_id"]
    assert client.put(f"/logs/{log_id}", headers=headers, json={"source": "identity", "event": "Updated impossible travel alert"}).status_code == 200

    vulnerability = client.post(
        "/vulnerabilities",
        headers=headers,
        json={
            "description": "Test exposed admin interface",
            "severity": "Medium",
            "status": "Open",
            "cve": "CVE-2099-0001",
            "affected_system": "Test SIEM Collector",
        },
    )
    assert vulnerability.status_code == 201
    vuln_id = vulnerability.json()["vuln_id"]
    assert client.put(f"/vulnerabilities/{vuln_id}", headers=headers, json={"status": "In Progress"}).status_code == 200

    response = client.post(
        "/responses",
        headers=headers,
        json={
            "incident_id": incident_id,
            "action_taken": "Disabled account and rotated credentials",
            "responder": "SOC Analyst",
            "time_taken": 35,
        },
    )
    assert response.status_code == 201
    response_id = response.json()["response_id"]
    assert client.put(f"/responses/{response_id}", headers=headers, json={"time_taken": 40}).status_code == 200

    timeline = client.get(f"/incidents/{incident_id}/timeline", headers=headers)
    assert timeline.status_code == 200
    assert [event["stage"] for event in timeline.json()["events"]] == [
        "Created",
        "Assigned",
        "Investigated",
        "Resolved",
        "Closed",
    ]

    ai_summary = client.get(f"/incidents/{incident_id}/ai-summary", headers=headers)
    assert ai_summary.status_code == 200
    assert ai_summary.json()["recommended_next_actions"]

    audit = client.get("/audit-logs", headers=headers)
    assert audit.status_code == 200
    assert any(row["action"] == "CREATE" for row in audit.json())
    assert any(row["action"] == "UPDATE" for row in audit.json())

    assert client.delete(f"/responses/{response_id}", headers=headers).status_code == 200
    assert client.delete(f"/vulnerabilities/{vuln_id}", headers=headers).status_code == 200
    assert client.delete(f"/logs/{log_id}", headers=headers).status_code == 200
    assert client.delete(f"/incidents/{incident_id}", headers=headers).status_code == 200
    assert client.delete(f"/systems/{system_id}", headers=headers).status_code == 200


def test_dashboard_search_and_reports():
    headers = auth_headers()
    dashboard = client.get("/dashboard/metrics", headers=headers)
    assert dashboard.status_code == 200
    dashboard_body = dashboard.json()
    assert dashboard_body["risk_level"] in {"Low", "Medium", "High", "Critical"}
    assert "incident_timeline" in dashboard_body
    assert client.get("/search?q=payment", headers=headers).status_code == 200

    csv_response = client.get("/reports/incidents.csv", headers=headers)
    assert csv_response.status_code == 200
    assert "text/csv" in csv_response.headers["content-type"]

    xlsx_response = client.get("/reports/incidents.xlsx", headers=headers)
    assert xlsx_response.status_code == 200
    assert xlsx_response.content.startswith(b"PK")

    pdf_response = client.get("/reports/incidents.pdf", headers=headers)
    assert pdf_response.status_code == 200
    assert pdf_response.content.startswith(b"%PDF")


def test_rbac_and_logout_flow():
    admin = auth_headers()
    analyst = analyst_headers()
    assert client.get("/users", headers=admin).status_code == 200
    assert client.get("/users", headers=analyst).status_code == 403

    login = client.post("/auth/login", json={"username": "admin", "password": "AdminPass123!"})
    token_pair = login.json()
    logout = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token_pair['access_token']}"},
        json={"refresh_token": token_pair["refresh_token"]},
    )
    assert logout.status_code == 200
