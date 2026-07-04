from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.crud import create_record, delete_record, get_record, list_records, update_record
from app.database import get_db
from app.dependencies import get_client_ip, get_current_user, require_roles
from app.models import Incident, Role, User
from app.schemas import APIMessage, ResponseCreate, ResponseOut, ResponseUpdate


router = APIRouter(prefix="/responses", tags=["Responses"])


def validate_incident(db: Session, incident_id: int | None) -> None:
    if incident_id is not None and not db.get(Incident, incident_id):
        raise HTTPException(status_code=400, detail="incident_id does not exist")


@router.get("", response_model=list[ResponseOut])
def list_responses(
    search: str | None = None,
    incident_id: int | None = None,
    sort_by: str | None = Query(default="response_id"),
    sort_order: str = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows, _total = list_records(db, "responses", search=search, sort_by=sort_by, sort_order=sort_order, page=page, page_size=page_size, filters={"incident_id": incident_id})
    return rows


@router.get("/{response_id}", response_model=ResponseOut)
def get_response(response_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return get_record(db, "responses", response_id)


@router.post("", response_model=ResponseOut, status_code=201)
def create_response(payload: ResponseCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst, Role.incident_manager))):
    data = payload.model_dump()
    validate_incident(db, data["incident_id"])
    return create_record(db, "responses", data, user=current_user, ip_address=get_client_ip(request))


@router.put("/{response_id}", response_model=ResponseOut)
def update_response(response_id: int, payload: ResponseUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst, Role.incident_manager))):
    data = payload.model_dump(exclude_unset=True)
    validate_incident(db, data.get("incident_id"))
    return update_record(db, "responses", response_id, data, user=current_user, ip_address=get_client_ip(request))


@router.delete("/{response_id}", response_model=APIMessage)
def delete_response(response_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin, Role.incident_manager))):
    delete_record(db, "responses", response_id, user=current_user, ip_address=get_client_ip(request))
    return APIMessage(detail="Response deleted")
