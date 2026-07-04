from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.crud import create_record, delete_record, get_record, list_records, update_record
from app.database import get_db
from app.dependencies import get_client_ip, get_current_user, require_roles
from app.models import Role, User
from app.schemas import APIMessage, VulnerabilityCreate, VulnerabilityOut, VulnerabilityUpdate


router = APIRouter(prefix="/vulnerabilities", tags=["Vulnerabilities"])


@router.get("", response_model=list[VulnerabilityOut])
def list_vulnerabilities(
    search: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    sort_by: str | None = Query(default="vuln_id"),
    sort_order: str = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows, _total = list_records(db, "vulnerabilities", search=search, sort_by=sort_by, sort_order=sort_order, page=page, page_size=page_size, filters={"severity": severity, "status": status})
    return rows


@router.get("/{vuln_id}", response_model=VulnerabilityOut)
def get_vulnerability(vuln_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return get_record(db, "vulnerabilities", vuln_id)


@router.post("", response_model=VulnerabilityOut, status_code=201)
def create_vulnerability(payload: VulnerabilityCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst))):
    return create_record(db, "vulnerabilities", payload.model_dump(exclude_none=True), user=current_user, ip_address=get_client_ip(request))


@router.put("/{vuln_id}", response_model=VulnerabilityOut)
def update_vulnerability(vuln_id: int, payload: VulnerabilityUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin, Role.soc_analyst))):
    return update_record(db, "vulnerabilities", vuln_id, payload.model_dump(exclude_unset=True), user=current_user, ip_address=get_client_ip(request))


@router.delete("/{vuln_id}", response_model=APIMessage)
def delete_vulnerability(vuln_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin))):
    delete_record(db, "vulnerabilities", vuln_id, user=current_user, ip_address=get_client_ip(request))
    return APIMessage(detail="Vulnerability deleted")
