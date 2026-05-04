from datetime import timedelta
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.db.connection import get_db
from app.models.schemas import Token, UserCreate, UserOut
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def _normalize_email(email: str) -> str:
    return email.strip().lower()

def _create_token(user_id: int, email: str) -> str:
    settings = get_settings()
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = {"sub": str(user_id), "email": email}
    return create_access_token(data=token_payload, expires_delta=expires_delta)


@router.post("/signup", status_code=201, response_model=UserOut)
def signup(
    body: UserCreate,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> UserOut:
    """Create a new user, returning their public profile."""
    repo = UserRepository()
    password_hash = get_password_hash(body.password)
    try:
        user_id = repo.create_user(conn, body.name.strip(), _normalize_email(body.email), password_hash)
    except ValueError as exc:
        if str(exc) == "duplicate_email":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        raise
    user_row = repo.get_user_by_id(conn, user_id)
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to return created user for {request.url.path}",
        )
    return user_row


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), conn: sqlite3.Connection = Depends(get_db)) -> Token:
    """Authenticate credentials and return a bearer token."""
    repo = UserRepository()
    user_row = repo.get_user_by_email(conn, _normalize_email(form_data.username))
    if not user_row or not verify_password(form_data.password, user_row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = _create_token(user_row["id"], user_row["email"])
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), conn: sqlite3.Connection = Depends(get_db)) -> dict:
    """Decode a bearer token and return the current user."""
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    try:
        resolved_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    user = UserRepository().get_user_by_id(conn, resolved_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
