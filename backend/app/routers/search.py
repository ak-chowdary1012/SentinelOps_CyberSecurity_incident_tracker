from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud import MODEL_CONFIG, list_records
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User


router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
def global_search(
    q: str = Query(min_length=1),
    page_size: int = Query(default=5, ge=1, le=25),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    results = {}
    for entity in MODEL_CONFIG:
        if entity == "users":
            continue
        rows, total = list_records(db, entity, search=q, page=1, page_size=page_size)
        results[entity] = {"total": total, "items": rows}
    return results
