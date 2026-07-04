from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.crud import create_record, delete_record, get_record, list_records, update_record
from app.database import get_db
from app.dependencies import get_client_ip, get_current_user, require_roles
from app.models import Role, System, User
from app.schemas import APIMessage, LogCreate, LogOut, LogUpdate


router = APIRouter(prefix="/logs", tags=["Logs"])


def validate_system(db: Session, system_id: int | None) -> None:
    if system_id is not None and not db.get(System, system_id):
        raise HTTPException(status_code=400, detail="system_id does not exist")


@router.get("", response_model=list[LogOut])
def list_logs(
    search: str | None = None,
    severity: str | None = None,
    source: str | None = None,
    sort_by: str | None = Query(default="timestamp"),
    sort_order: str = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows, _total = list_records(db, "logs", search=search, sort_by=sort_by, sort_order=sort_order, page=page, page_size=page_size, filters={"severity": severity, "source": source})
    return rows


@router.get("/{log_id}", response_model=LogOut)
def get_log(log_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return get_record(db, "logs", log_id)


@router.post("", response_model=LogOut, status_code=201)
def create_log(payload: LogCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst))):
    data = payload.model_dump(exclude_none=True)
    validate_system(db, data.get("system_id"))
    return create_record(db, "logs", data, user=current_user, ip_address=get_client_ip(request))


@router.put("/{log_id}", response_model=LogOut)
def update_log(log_id: int, payload: LogUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst))):
    data = payload.model_dump(exclude_unset=True)
    validate_system(db, data.get("system_id"))
    return update_record(db, "logs", log_id, data, user=current_user, ip_address=get_client_ip(request))


@router.delete("/{log_id}", response_model=APIMessage)
def delete_log(log_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin))):
    delete_record(db, "logs", log_id, user=current_user, ip_address=get_client_ip(request))
    return APIMessage(detail="Log deleted")
