
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User


def register_user(
    db: Session,
    full_name: str,
    email: str,
    password: str,
) -> User:
    normalized_email = email.strip().lower()

    existing_user = db.scalar(
        select(User).where(
            User.email == normalized_email
        )
    )

    if existing_user:
        raise ValueError("Email is already registered")

    user = User(
        full_name=full_name.strip(),
        email=normalized_email,
        password_hash=hash_password(password),
        role="CUSTOMER",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    normalized_email = email.strip().lower()

    user = db.scalar(
        select(User).where(
            User.email == normalized_email
        )
    )

    if not user or not verify_password(
        password,
        user.password_hash,
    ):
        return None

    if not user.is_active:
        return None

    access_token = create_access_token(
        user.id,
        user.role,
    )

    refresh_token, token_id, expires_at = (
        create_refresh_token(user.id, user.role)
    )

    stored_token = RefreshToken(
        jti=token_id,
        users_id=user.id,
        expires_at=expires_at,
    )

    db.add(stored_token)
    db.commit()

    return user, access_token, refresh_token
