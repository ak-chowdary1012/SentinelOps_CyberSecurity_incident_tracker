from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, field_validator

from app.models import IncidentStatus, Role, Severity, SystemStatus, VulnerabilityStatus


class APIMessage(BaseModel):
    detail: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    role: Role = Role.viewer
    contact: str = Field(min_length=3, max_length=150)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    role: Role | None = None
    contact: str | None = Field(default=None, min_length=3, max_length=150)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None


class UserOut(UserBase):
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SystemBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    ip_address: IPvAnyAddress
    department: str = Field(min_length=1, max_length=80)
    status: SystemStatus = SystemStatus.online
    criticality: Severity = Severity.medium

    @field_validator("ip_address", mode="after")
    @classmethod
    def stringify_ip(cls, value: IPvAnyAddress) -> str:
        return str(value)


class SystemCreate(SystemBase):
    pass


class SystemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    ip_address: IPvAnyAddress | None = None
    department: str | None = Field(default=None, min_length=1, max_length=80)
    status: SystemStatus | None = None
    criticality: Severity | None = None

    @field_validator("ip_address", mode="after")
    @classmethod
    def stringify_optional_ip(cls, value: IPvAnyAddress | None) -> str | None:
        return str(value) if value is not None else None


class SystemOut(SystemBase):
    system_id: int
    model_config = ConfigDict(from_attributes=True)


class IncidentBase(BaseModel):
    date: datetime | None = None
    type: str = Field(min_length=1, max_length=80)
    severity: Severity
    status: IncidentStatus = IncidentStatus.open
    description: str | None = None
    resolved_at: datetime | None = None


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    date: datetime | None = None
    type: str | None = Field(default=None, min_length=1, max_length=80)
    severity: Severity | None = None
    status: IncidentStatus | None = None
    description: str | None = None
    resolved_at: datetime | None = None


class IncidentOut(IncidentBase):
    incident_id: int
    date: datetime
    model_config = ConfigDict(from_attributes=True)


class LogBase(BaseModel):
    timestamp: datetime | None = None
    event: str = Field(min_length=1)
    source: str = Field(min_length=1, max_length=80)
    severity: Severity = Severity.low
    system_id: int | None = None


class LogCreate(LogBase):
    pass


class LogUpdate(BaseModel):
    timestamp: datetime | None = None
    event: str | None = Field(default=None, min_length=1)
    source: str | None = Field(default=None, min_length=1, max_length=80)
    severity: Severity | None = None
    system_id: int | None = None


class LogOut(LogBase):
    log_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class VulnerabilityBase(BaseModel):
    description: str = Field(min_length=1)
    severity: Severity
    status: VulnerabilityStatus = VulnerabilityStatus.open
    cve: str | None = Field(default=None, max_length=32)
    affected_system: str | None = Field(default=None, max_length=100)


class VulnerabilityCreate(VulnerabilityBase):
    pass


class VulnerabilityUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1)
    severity: Severity | None = None
    status: VulnerabilityStatus | None = None
    cve: str | None = Field(default=None, max_length=32)
    affected_system: str | None = Field(default=None, max_length=100)


class VulnerabilityOut(VulnerabilityBase):
    vuln_id: int
    model_config = ConfigDict(from_attributes=True)


class ResponseBase(BaseModel):
    incident_id: int
    action_taken: str = Field(min_length=1)
    responder: str = Field(min_length=1, max_length=100)
    time_taken: int = Field(ge=0)


class ResponseCreate(ResponseBase):
    pass


class ResponseUpdate(BaseModel):
    incident_id: int | None = None
    action_taken: str | None = Field(default=None, min_length=1)
    responder: str | None = Field(default=None, min_length=1, max_length=100)
    time_taken: int | None = Field(default=None, ge=0)


class ResponseOut(ResponseBase):
    response_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AuditLogOut(BaseModel):
    audit_id: int
    user_id: int | None
    username: str
    action: str
    entity: str
    entity_id: str | None
    before_value: dict[str, Any] | None
    after_value: dict[str, Any] | None
    ip_address: str | None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class DashboardMetrics(BaseModel):
    threat_level: str
    organizational_risk_score: int
    risk_level: str
    risk_explanation: str
    critical_incidents: int
    open_incidents: int
    resolved_incidents: int
    average_resolution_minutes: float
    critical_vulnerabilities: int
    systems_online: int
    security_alerts_today: int
    analysts_online: int
    systems_protected: int
    incident_severity: dict[str, int]
    incident_trend: dict[str, int]
    vulnerability_distribution: dict[str, int]
    system_health: dict[str, int]
    top_attack_types: dict[str, int]
    incident_timeline: list[dict[str, Any]]
    recent_security_events: list[dict[str, Any]]
    recent_activities: list[AuditLogOut]


class Page(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int


class IncidentTimelineEvent(BaseModel):
    stage: str
    status: str
    timestamp: datetime | None
    description: str


class IncidentTimeline(BaseModel):
    incident_id: int
    current_status: str
    events: list[IncidentTimelineEvent]


class IncidentAISummary(BaseModel):
    incident_id: int
    summary: str
    recommended_severity: str
    likely_category: str
    recommended_next_actions: list[str]
    risk_rationale: str
