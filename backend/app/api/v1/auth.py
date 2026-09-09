from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.security import (
    create_access_token,
    get_current_admin,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.app.db.session import get_db
from backend.app.models.role import Role
from backend.app.models.user import User

router = APIRouter(tags=["auth"])
DatabaseSession = Annotated[Session, Depends(get_db)]


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserStatusUpdate(BaseModel):
    is_active: bool


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DatabaseSession) -> TokenResponse:
    existing = db.scalar(
        select(User).where(or_(User.username == payload.username, User.email == payload.email))
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists.")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    if db.scalar(select(func.count(User.id))) == 0:
        user.roles.append(Role(name="admin", description="Platform administrator"))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists.",
        ) from exc
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DatabaseSession) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or user.password_hash is None or not verify_password(
        payload.password, user.password_hash
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive.")
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/auth/me")
def me(user: Annotated[User, Depends(get_current_user)]) -> dict[str, object]:
    return {"id": user.id, "username": user.username, "email": user.email}


@router.get("/admin/users")
def list_users(
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_admin)],
) -> list[dict[str, object]]:
    users = db.scalars(select(User).order_by(User.id))
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "roles": [role.name for role in user.roles],
        }
        for user in users
    ]


@router.patch("/admin/users/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: DatabaseSession,
    admin: Annotated[User, Depends(get_current_admin)],
) -> dict[str, object]:
    if user_id == admin.id and not payload.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot deactivate themselves.",
        )

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "roles": [role.name for role in user.roles],
    }
