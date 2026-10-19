

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.db.session import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    register_user,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication and RBAC"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    request: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        return register_user(
            db=db,
            full_name=request.full_name,
            email=str(request.email),
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    result = authenticate_user(
        db,
        str(request.email),
        request.password,
    )

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    _, access_token, refresh_token = result

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise ValueError("Wrong token type")

        token_id = payload["jti"]
        user_id = int(payload["sub"])

    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        ) from None

    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.jti == token_id,
            RefreshToken.users_id == user_id,
        )
    )

    now = datetime.now(timezone.utc)

    if stored_token is None or stored_token.revoked:
        raise HTTPException(
            status_code=401,
            detail="Refresh token is invalid or revoked",
        )

    expiry = stored_token.expires_at

    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry <= now:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired",
        )

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User account is unavailable",
        )

    # Rotate the refresh token so the old one cannot be reused.
    stored_token.revoked = True

    access_token = create_access_token(
        user.id,
        user.role,
    )

    new_refresh, new_jti, new_expiry = (
        create_refresh_token(user.id, user.role)
    )

    db.add(
        RefreshToken(
            jti=new_jti,
            users_id=user.id,
            expires_at=new_expiry,
        )
    )

    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
    )


@router.post("/logout")
def logout(
    request: LogoutRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise ValueError("Wrong token type")

        token_id = payload["jti"]

    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        ) from None

    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.jti == token_id,
            RefreshToken.users_id == current_user.id,
        )
    )

    if stored_token is not None:
        stored_token.revoked = True
        db.commit()

    return {
        "success": True,
        "message": "Logged out successfully",
        "data": None,
    }


@router.get("/me", response_model=UserResponse)
def get_my_account(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return current_user

