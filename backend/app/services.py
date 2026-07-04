import csv
import io
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    AuditLog,
    Incident,
    IncidentStatus,
    Log,
    RefreshToken,
    Role,
    Severity,
    System,
    SystemStatus,
    User,
    Vulnerability,
)
from app.security import create_access_token, create_refresh_token, hash_token, verify_password
from app.config import get_settings


settings = get_settings()


def model_to_dict(obj: Any) -> dict[str, Any]:
    data = {}
    for column in obj.__table__.columns:
        if column.name in {"hashed_password", "token_hash"}:
            continue
        value = getattr(obj, column.name)
        if isinstance(value, datetime):
            data[column.name] = value.isoformat()
        elif hasattr(value, "value"):
            data[column.name] = value.value
        else:
            data[column.name] = value
    return data


def normalize_json(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None
    normalized = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            normalized[key] = value.isoformat()
        elif hasattr(value, "value"):
            normalized[key] = value.value
        else:
            normalized[key] = value
    return normalized


def write_audit(
    db: Session,
    *,
    user: User | None,
    action: str,
    entity: str,
    entity_id: str | int | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    audit = AuditLog(
        user_id=user.user_id if user else None,
        username=user.username if user else "system",
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id is not None else None,
        before_value=normalize_json(before),
        after_value=normalize_json(after),
        ip_address=ip_address,
    )
    db.add(audit)
    return audit


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        return None
    return user


def issue_tokens(db: Session, user: User) -> tuple[str, str]:
    access_token = create_access_token(user.username, user.role.value)
    refresh_token = create_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days)
    db.add(RefreshToken(user_id=user.user_id, token_hash=hash_token(refresh_token), expires_at=expires_at))
    return access_token, refresh_token


def calculate_risk_score(
    *,
    critical_incidents: int,
    open_incidents: int,
    critical_vulnerabilities: int,
    average_resolution_minutes: float,
) -> tuple[int, str, str]:
    score = min(
        100,
        critical_incidents * 18
        + open_incidents * 8
        + critical_vulnerabilities * 16
        + int(min(average_resolution_minutes, 720) / 24),
    )
    if score >= 75:
        level = "Critical"
    elif score >= 50:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"
    explanation = (
        f"Score {score}/100 from {critical_incidents} critical incidents, "
        f"{open_incidents} open investigations, {critical_vulnerabilities} critical vulnerabilities, "
        f"and {average_resolution_minutes} minute average resolution time."
    )
    return score, level, explanation


def build_incident_timeline(incident: Incident) -> list[dict[str, Any]]:
    stage_order = [
        ("Created", "Open", incident.date, "Incident record created and queued for SOC triage."),
        ("Assigned", "Investigating", incident.date + timedelta(minutes=15), "Incident assigned to analyst queue."),
        ("Investigated", "Investigating", incident.date + timedelta(minutes=45), "Evidence review and containment analysis in progress."),
        ("Resolved", "Resolved", incident.resolved_at, "Remediation completed and validation checks passed."),
        ("Closed", "Closed", incident.resolved_at + timedelta(minutes=30) if incident.resolved_at else None, "Post-incident review completed."),
    ]
    status_rank = {
        IncidentStatus.open: 1,
        IncidentStatus.investigating: 3,
        IncidentStatus.contained: 3,
        IncidentStatus.resolved: 4,
        IncidentStatus.closed: 5,
    }
    current_rank = status_rank.get(incident.status, 1)
    events = []
    for index, (stage, status, timestamp, description) in enumerate(stage_order, start=1):
        events.append(
            {
                "stage": stage,
                "status": "Complete" if index <= current_rank else "Pending",
                "timestamp": timestamp,
                "description": description,
            }
        )
    return events


def summarize_incident(incident: Incident) -> dict[str, Any]:
    text = f"{incident.type} {incident.description or ''}".lower()
    likely_category = "Threat Activity"
    if any(term in text for term in ["phishing", "credential", "mfa", "login"]):
        likely_category = "Identity Threat"
    elif any(term in text for term in ["malware", "ransomware", "beacon", "edr"]):
        likely_category = "Endpoint Compromise"
    elif any(term in text for term in ["ddos", "traffic", "waf"]):
        likely_category = "Network Attack"

    recommended_severity = incident.severity.value
    if incident.status in {IncidentStatus.open, IncidentStatus.investigating} and incident.severity in {
        Severity.high,
        Severity.critical,
    }:
        next_actions = [
            "Confirm affected assets and business owner.",
            "Collect authentication, endpoint, and network telemetry.",
            "Apply containment before eradication if lateral movement is suspected.",
        ]
    else:
        next_actions = [
            "Validate remediation evidence.",
            "Document timeline and lessons learned.",
            "Monitor for recurrence over the next reporting period.",
        ]

    summary = (
        f"{incident.type} is currently {incident.status.value.lower()} with "
        f"{incident.severity.value.lower()} severity. The available details indicate "
        f"{likely_category.lower()} requiring SOC review."
    )
    rationale = (
        f"Recommendation is based on current severity '{incident.severity.value}', "
        f"status '{incident.status.value}', and keywords in the incident narrative."
    )
    return {
        "incident_id": incident.incident_id,
        "summary": summary,
        "recommended_severity": recommended_severity,
        "likely_category": likely_category,
        "recommended_next_actions": next_actions,
        "risk_rationale": rationale,
    }


def get_dashboard_metrics(db: Session) -> dict[str, Any]:
    critical_incidents = db.query(Incident).filter(Incident.severity == Severity.critical).count()
    open_incidents = db.query(Incident).filter(Incident.status.in_([IncidentStatus.open, IncidentStatus.investigating])).count()
    resolved_incidents = db.query(Incident).filter(Incident.status.in_([IncidentStatus.resolved, IncidentStatus.closed])).count()
    critical_vulnerabilities = db.query(Vulnerability).filter(Vulnerability.severity == Severity.critical).count()
    systems_online = db.query(System).filter(System.status == SystemStatus.online).count()
    systems_protected = db.query(System).count()
    analysts_online = db.query(User).filter(User.is_active.is_(True), User.role.in_([Role.admin, Role.soc_analyst, Role.incident_manager])).count()
    today = datetime.now(timezone.utc).date()
    security_alerts_today = db.query(Log).filter(func.date(Log.timestamp) == today).count()

    incident_severity = Counter(
        severity for (severity,) in db.query(Incident.severity).all()
    )
    vulnerability_distribution = Counter(
        severity for (severity,) in db.query(Vulnerability.severity).all()
    )
    system_health = Counter(status for (status,) in db.query(System.status).all())
    top_attack_types = Counter(kind for (kind,) in db.query(Incident.type).all()).most_common(5)

    trend_rows = (
        db.query(func.date(Incident.date), func.count(Incident.incident_id))
        .group_by(func.date(Incident.date))
        .order_by(func.date(Incident.date))
        .limit(30)
        .all()
    )

    resolved = db.query(Incident).filter(Incident.resolved_at.isnot(None)).all()
    durations = [
        (incident.resolved_at - incident.date).total_seconds() / 60
        for incident in resolved
        if incident.resolved_at and incident.date
    ]
    average_resolution = round(sum(durations) / len(durations), 2) if durations else 0.0
    threat_level = "Critical" if critical_incidents or critical_vulnerabilities else "Elevated" if open_incidents else "Normal"
    risk_score, risk_level, risk_explanation = calculate_risk_score(
        critical_incidents=critical_incidents,
        open_incidents=open_incidents,
        critical_vulnerabilities=critical_vulnerabilities,
        average_resolution_minutes=average_resolution,
    )

    recent_events = (
        db.query(Log)
        .order_by(Log.timestamp.desc())
        .limit(8)
        .all()
    )
    recent_activities = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(8)
        .all()
    )

    return {
        "threat_level": threat_level,
        "organizational_risk_score": risk_score,
        "risk_level": risk_level,
        "risk_explanation": risk_explanation,
        "critical_incidents": critical_incidents,
        "open_incidents": open_incidents,
        "resolved_incidents": resolved_incidents,
        "average_resolution_minutes": average_resolution,
        "critical_vulnerabilities": critical_vulnerabilities,
        "systems_online": systems_online,
        "security_alerts_today": security_alerts_today,
        "analysts_online": analysts_online,
        "systems_protected": systems_protected,
        "incident_severity": {key.value if hasattr(key, "value") else str(key): value for key, value in incident_severity.items()},
        "incident_trend": {str(day): count for day, count in trend_rows},
        "vulnerability_distribution": {key.value if hasattr(key, "value") else str(key): value for key, value in vulnerability_distribution.items()},
        "system_health": {key.value if hasattr(key, "value") else str(key): value for key, value in system_health.items()},
        "top_attack_types": dict(top_attack_types),
        "incident_timeline": [
            {
                "incident_id": incident.incident_id,
                "type": incident.type,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "events": build_incident_timeline(incident),
            }
            for incident in db.query(Incident).order_by(Incident.date.desc()).limit(5).all()
        ],
        "recent_security_events": [
            {
                "timestamp": event.timestamp.isoformat(),
                "event": event.event,
                "source": event.source,
                "severity": event.severity.value,
                "system_id": event.system_id,
            }
            for event in recent_events
        ],
        "recent_activities": recent_activities,
    }


def rows_to_csv(rows: list[dict[str, Any]]) -> str:
    output = io.StringIO()
    if not rows:
        return ""
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
