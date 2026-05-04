from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password
from app.db.connection import get_db
from app.models.schemas import Token, UserCreate, UserOut
from app.repositories.user_repository import UserRepository
import sqlite3

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _public_user_row(user_row: dict) -> dict:
    user_data = {k: v for k, v in user_row.items() if k != "password_hash"}
    return user_data


@router.post("/signup", status_code=201, response_model=UserOut)
def signup(body: UserCreate, conn: sqlite3.Connection = Depends(get_db)) -> UserOut:
    password_hash = get_password_hash(body.password)
    repo = UserRepository()
    try:
        user_id = repo.create_user(conn, body.name.strip(), body.email.lower(), password_hash)
    except ValueError as exc:
        if exc.args and exc.args[0] == "duplicate_email":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        raise
    user_row = repo.get_user_by_id(conn, user_id)
    if not user_row:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to return created user")
    return UserOut(**_public_user_row(user_row))


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), conn: sqlite3.Connection = Depends(get_db)) -> Token:
    repo = UserRepository()
    normalized_email = form_data.username.lower()
    user_row = repo.get_user_by_email(conn, normalized_email)
    if not user_row or not verify_password(form_data.password, user_row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    payload = {"sub": str(user_row["id"]), "email": user_row["email"]}
    access_token = create_access_token(payload)
    return Token(access_token=access_token, token_type="bearer")


def get_current_user(token: str = Depends(oauth2_scheme), conn: sqlite3.Connection = Depends(get_db)) -> dict:
    try:
        payload = decode_access_token(token)
    except HTTPException:
        raise
    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    try:
        resolved_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    user_row = UserRepository().get_user_by_id(conn, resolved_id)
    if not user_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return _public_user_row(user_row)
