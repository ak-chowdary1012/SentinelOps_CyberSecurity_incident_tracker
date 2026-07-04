from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import AuditLog, Role, User
from app.schemas import AuditLogOut


router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    action: str | None = None,
    entity: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.admin, Role.incident_manager)),
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity:
        query = query.filter(AuditLog.entity == entity)
    return query.order_by(AuditLog.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
