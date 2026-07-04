from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.crud import create_record, delete_record, get_record, list_records, update_record
from app.database import get_db
from app.dependencies import get_client_ip, get_current_user, require_roles
from app.models import Role, User
from app.schemas import APIMessage, SystemCreate, SystemOut, SystemUpdate


router = APIRouter(prefix="/systems", tags=["Systems"])


@router.get("", response_model=list[SystemOut])
def list_systems(
    search: str | None = None,
    department: str | None = None,
    status: str | None = None,
    sort_by: str | None = Query(default="system_id"),
    sort_order: str = "asc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows, _total = list_records(
        db,
        "systems",
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        filters={"department": department, "status": status},
    )
    return rows


@router.get("/{system_id}", response_model=SystemOut)
def get_system(system_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return get_record(db, "systems", system_id)


@router.post("", response_model=SystemOut, status_code=201)
def create_system(
    payload: SystemCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst, Role.incident_manager)),
):
    return create_record(db, "systems", payload.model_dump(), user=current_user, ip_address=get_client_ip(request))


@router.put("/{system_id}", response_model=SystemOut)
def update_system(
    system_id: int,
    payload: SystemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst, Role.incident_manager)),
):
    return update_record(db, "systems", system_id, payload.model_dump(exclude_unset=True), user=current_user, ip_address=get_client_ip(request))


@router.delete("/{system_id}", response_model=APIMessage)
def delete_system(
    system_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.admin)),
):
    delete_record(db, "systems", system_id, user=current_user, ip_address=get_client_ip(request))
    return APIMessage(detail="System deleted")
