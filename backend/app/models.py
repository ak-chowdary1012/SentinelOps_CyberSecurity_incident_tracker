from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, Enum):
    admin = "Admin"
    soc_analyst = "SOC Analyst"
    incident_manager = "Incident Manager"
    viewer = "Viewer"


class Severity(str, Enum):
    critical = "Critical"
    high = "High"
    medium = "Medium"
    low = "Low"


class IncidentStatus(str, Enum):
    open = "Open"
    investigating = "Investigating"
    contained = "Contained"
    resolved = "Resolved"
    closed = "Closed"


class VulnerabilityStatus(str, Enum):
    open = "Open"
    in_progress = "In Progress"
    fixed = "Fixed"
    accepted = "Risk Accepted"


class SystemStatus(str, Enum):
    online = "Online"
    degraded = "Degraded"
    offline = "Offline"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), nullable=False, default=Role.viewer)
    contact: Mapped[str] = mapped_column(String(150), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class System(Base):
    __tablename__ = "systems"
    __table_args__ = (
        UniqueConstraint("ip_address", name="uq_systems_ip_address"),
        Index("ix_systems_department", "department"),
    )

    system_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    department: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[SystemStatus] = mapped_column(SQLEnum(SystemStatus), nullable=False, default=SystemStatus.online)
    criticality: Mapped[Severity] = mapped_column(SQLEnum(Severity), nullable=False, default=Severity.medium)

    logs: Mapped[list["Log"]] = relationship("Log", back_populates="system", cascade="all, delete-orphan")


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_status_severity", "status", "severity"),
        Index("ix_incidents_date", "date"),
    )

    incident_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    severity: Mapped[Severity] = mapped_column(SQLEnum(Severity), nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(SQLEnum(IncidentStatus), nullable=False, default=IncidentStatus.open)
    description: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    responses: Mapped[list["Response"]] = relationship(
        "Response", back_populates="incident", cascade="all, delete-orphan"
    )


class Log(Base):
    __tablename__ = "logs"
    __table_args__ = (Index("ix_logs_timestamp_source", "timestamp", "source"),)

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    event: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[Severity] = mapped_column(SQLEnum(Severity), nullable=False, default=Severity.low)
    system_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("systems.system_id", ondelete="SET NULL"))

    system: Mapped[System | None] = relationship("System", back_populates="logs")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    __table_args__ = (Index("ix_vulnerabilities_status_severity", "status", "severity"),)

    vuln_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(SQLEnum(Severity), nullable=False)
    status: Mapped[VulnerabilityStatus] = mapped_column(
        SQLEnum(VulnerabilityStatus), nullable=False, default=VulnerabilityStatus.open
    )
    cve: Mapped[str | None] = mapped_column(String(32), index=True)
    affected_system: Mapped[str | None] = mapped_column(String(100))


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (
        CheckConstraint("time_taken >= 0", name="ck_responses_time_taken_non_negative"),
        Index("ix_responses_incident_id", "incident_id"),
    )

    response_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(Integer, ForeignKey("incidents.incident_id", ondelete="CASCADE"), nullable=False)
    action_taken: Mapped[str] = mapped_column(Text, nullable=False)
    responder: Mapped[str] = mapped_column(String(100), nullable=False)
    time_taken: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    incident: Mapped[Incident] = relationship("Incident", back_populates="responses")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_timestamp_action", "timestamp", "action"),)

    audit_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    username: Mapped[str] = mapped_column(String(50), nullable=False, default="system")
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    entity: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(80))
    before_value: Mapped[dict | None] = mapped_column(JSON)
    after_value: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (Index("ix_refresh_tokens_expires_at", "expires_at"),)

    token_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")
