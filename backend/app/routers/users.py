from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import delete_record, get_record, list_records, update_record
from app.database import get_db
from app.dependencies import get_client_ip, get_current_user, require_roles
from app.models import Role, User
from app.schemas import APIMessage, UserCreate, UserOut, UserUpdate
from app.security import hash_password
from app.services import model_to_dict, write_audit


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserOut])
def list_users(search: str | None = None, role: str | None = None, sort_by: str | None = Query(default="user_id"), sort_order: str = "asc", page: int = Query(default=1, ge=1), page_size: int = Query(default=25, ge=1, le=100), db: Session = Depends(get_db), _: User = Depends(require_roles(Role.admin))):
    rows, _total = list_records(db, "users", search=search, sort_by=sort_by, sort_order=sort_order, page=page, page_size=page_size, filters={"role": role})
    return rows


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_roles(Role.admin))):
    return get_record(db, "users", user_id)


@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin))):
    user = User(**payload.model_dump(exclude={"password"}), hashed_password=hash_password(payload.password))
    try:
        db.add(user)
        db.flush()
        write_audit(db, user=current_user, action="CREATE", entity="users", entity_id=user.user_id, after=model_to_dict(user), ip_address=get_client_ip(request))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="User conflicts with an existing record") from exc
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin))):
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        data["hashed_password"] = hash_password(data.pop("password"))
    return update_record(db, "users", user_id, data, user=current_user, ip_address=get_client_ip(request))


@router.delete("/{user_id}", response_model=APIMessage)
def delete_user(user_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.admin))):
    delete_record(db, "users", user_id, user=current_user, ip_address=get_client_ip(request))
    return APIMessage(detail="User deleted")
