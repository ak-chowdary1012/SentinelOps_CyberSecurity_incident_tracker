import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE = "http://127.0.0.1:8000"


def request(method: str, path: str, token: str | None = None, body: dict | None = None):
    headers = {"Content-Type": "application/json"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body).encode()
    req = Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    with urlopen(req, timeout=10) as response:
        raw = response.read()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.status, json.loads(raw.decode()), response.headers, raw
        return response.status, raw, response.headers, raw


def wait_for_api() -> None:
    for _ in range(40):
        try:
            status, body, _, _ = request("GET", "/health")
            if status == 200 and body.get("status") == "ok":
                return
        except (HTTPError, URLError, TimeoutError):
            pass
        time.sleep(0.25)
    raise RuntimeError("API did not become healthy")


def main() -> None:
    wait_for_api()
    _, login, _, _ = request("POST", "/auth/login", body={"username": "admin", "password": "AdminPass123!"})
    token = login["access_token"]

    suffix = int(time.time())
    status, system, _, _ = request(
        "POST",
        "/systems",
        token,
        {
            "name": f"Fresh Clone Sensor {suffix}",
            "ip_address": f"10.88.{suffix % 200}.{suffix % 250}",
            "department": "Security",
            "status": "Online",
            "criticality": "High",
        },
    )
    assert status == 201
    system_id = system["system_id"]

    status, incident, _, _ = request(
        "POST",
        "/incidents",
        token,
        {
            "date": "2026-07-21T10:00:00Z",
            "type": "Fresh Clone Validation",
            "severity": "High",
            "status": "Open",
            "description": "Live API smoke incident.",
        },
    )
    assert status == 201
    incident_id = incident["incident_id"]

    status, search, _, _ = request("GET", f"/search?{urlencode({'q': 'Fresh Clone'})}", token)
    assert status == 200
    assert search["incidents"]["total"] >= 1

    status, audit, _, _ = request("GET", "/audit-logs", token)
    assert status == 200
    assert any(row["action"] == "CREATE" for row in audit)

    export_results = {}
    for fmt, marker in {"csv": b"incident_id", "xlsx": b"PK", "pdf": b"%PDF"}.items():
        status, _, headers, raw = request("GET", f"/reports/incidents.{fmt}", token)
        assert status == 200
        assert raw.startswith(marker) or marker in raw[:200]
        export_results[fmt] = headers.get("content-type")

    request("DELETE", f"/incidents/{incident_id}", token)
    request("DELETE", f"/systems/{system_id}", token)

    print(f"login_token_type: {login['token_type']}")
    print(f"created_system_id: {system_id}")
    print(f"created_incident_id: {incident_id}")
    print(f"search_incidents_total: {search['incidents']['total']}")
    print(f"audit_rows: {len(audit)}")
    print(f"exports: {export_results}")
    print("live api smoke: ok")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"live api smoke failed: {exc}", file=sys.stderr)
        raise
