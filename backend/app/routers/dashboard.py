from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import DashboardMetrics
from app.services import get_dashboard_metrics


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
def metrics(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return get_dashboard_metrics(db)
