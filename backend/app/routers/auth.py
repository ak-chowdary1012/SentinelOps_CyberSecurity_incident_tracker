from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

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
LOGIN_WINDOW_SECONDS = 60
LOGIN_MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300
_ip_attempts: dict[str, deque[datetime]] = defaultdict(deque)
_user_failures: dict[str, tuple[int, datetime | None]] = {}


def is_expired(expires_at: datetime) -> bool:
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < datetime.now(timezone.utc)


def _rate_limit_key(request: Request) -> str:
    return get_client_ip(request) or "unknown"


def enforce_login_rate_limit(request: Request) -> None:
    now = datetime.now(timezone.utc)
    attempts = _ip_attempts[_rate_limit_key(request)]
    while attempts and (now - attempts[0]).total_seconds() > LOGIN_WINDOW_SECONDS:
        attempts.popleft()
    if len(attempts) >= LOGIN_MAX_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts")


def record_ip_failure(request: Request) -> None:
    _ip_attempts[_rate_limit_key(request)].append(datetime.now(timezone.utc))


def enforce_username_lockout(username: str) -> None:
    _failures, locked_until = _user_failures.get(username, (0, None))
    if locked_until and locked_until > datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Account temporarily locked")


def record_login_failure(username: str) -> None:
    failures, _locked_until = _user_failures.get(username, (0, None))
    failures += 1
    locked_until = None
    if failures >= LOGIN_MAX_ATTEMPTS:
        locked_until = datetime.now(timezone.utc) + timedelta(seconds=LOCKOUT_SECONDS)
    _user_failures[username] = (failures, locked_until)


def clear_login_failures(username: str) -> None:
    _user_failures.pop(username, None)


def authenticate_and_issue_token_pair(
    request: Request,
    username: str,
    password: str,
    db: Session,
) -> TokenPair:
    enforce_login_rate_limit(request)
    enforce_username_lockout(username)
    user = authenticate(db, username, password)
    if not user:
        record_ip_failure(request)
        record_login_failure(username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    clear_login_failures(username)
    access_token, refresh_token = issue_tokens(db, user)
    write_audit(db, user=user, action="LOGIN", entity="auth", ip_address=get_client_ip(request))
    db.commit()
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenPair)
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    return authenticate_and_issue_token_pair(request, payload.username, payload.password, db)


@router.post("/token", response_model=TokenPair)
def token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return authenticate_and_issue_token_pair(request, form_data.username, form_data.password, db)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    enforce_login_rate_limit(request)
    token_hash = hash_token(payload.refresh_token)
    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash, RefreshToken.revoked.is_(False))
        .first()
    )
    if not token or is_expired(token.expires_at):
        record_ip_failure(request)
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
