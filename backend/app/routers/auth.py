from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_client_ip, get_current_user
from app.models import RefreshToken, User
from app.schemas import APIMessage, LoginRequest, RefreshRequest, TokenPair
from app.security import hash_token
from app.services import authenticate, issue_tokens, write_audit


router = APIRouter(prefix="/auth", tags=["Authentication"])


def is_expired(expires_at: datetime) -> bool:
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < datetime.now(timezone.utc)


@router.post("/login", response_model=TokenPair)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    access_token, refresh_token = issue_tokens(db, user)
    write_audit(db, user=user, action="LOGIN", entity="auth", ip_address=get_client_ip(request))
    db.commit()
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hash_token(payload.refresh_token)
    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash, RefreshToken.revoked.is_(False))
        .first()
    )
    if not token or is_expired(token.expires_at):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    token.revoked = True
    access_token, refresh_token = issue_tokens(db, token.user)
    db.commit()
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", response_model=APIMessage)
def logout(
    payload: RefreshRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    token = db.query(RefreshToken).filter(RefreshToken.token_hash == hash_token(payload.refresh_token)).first()
    if token:
        token.revoked = True
    write_audit(db, user=current_user, action="LOGOUT", entity="auth", ip_address=get_client_ip(request))
    db.commit()
    return APIMessage(detail="Logged out")
