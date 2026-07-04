from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.crud import create_record, delete_record, get_record, list_records, update_record
from app.database import get_db
from app.dependencies import get_client_ip, get_current_user, require_roles
from app.models import Role, User
from app.schemas import APIMessage, IncidentAISummary, IncidentCreate, IncidentOut, IncidentTimeline, IncidentUpdate
from app.services import build_incident_timeline, summarize_incident


router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    search: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    sort_by: str | None = Query(default="incident_id"),
    sort_order: str = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows, _total = list_records(
        db,
        "incidents",
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        filters={"severity": severity, "status": status},
    )
    return rows


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return get_record(db, "incidents", incident_id)


@router.get("/{incident_id}/timeline", response_model=IncidentTimeline)
def get_incident_timeline(incident_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    incident = get_record(db, "incidents", incident_id)
    return {
        "incident_id": incident.incident_id,
        "current_status": incident.status.value,
        "events": build_incident_timeline(incident),
    }


@router.get("/{incident_id}/ai-summary", response_model=IncidentAISummary)
def get_incident_ai_summary(incident_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    incident = get_record(db, "incidents", incident_id)
    return summarize_incident(incident)


@router.post("", response_model=IncidentOut, status_code=201)
def create_incident(
    payload: IncidentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst, Role.incident_manager)),
):
    return create_record(db, "incidents", payload.model_dump(exclude_none=True), user=current_user, ip_address=get_client_ip(request))


@router.put("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst, Role.incident_manager)),
):
    return update_record(db, "incidents", incident_id, payload.model_dump(exclude_unset=True), user=current_user, ip_address=get_client_ip(request))


@router.delete("/{incident_id}", response_model=APIMessage)
def delete_incident(
    incident_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.admin, Role.incident_manager)),
):
    delete_record(db, "incidents", incident_id, user=current_user, ip_address=get_client_ip(request))
    return APIMessage(detail="Incident deleted")
