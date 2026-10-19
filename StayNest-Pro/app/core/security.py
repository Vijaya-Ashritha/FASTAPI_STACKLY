
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from jose import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, stored_hash: str) -> bool:
    return password_hash.verify(plain_password, stored_hash)


def create_access_token(user_id: int, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expires_at,
        "jti": str(uuid4()),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_refresh_token(user_id: int, role: str):
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    token_id = str(uuid4())

    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
        "exp": expires_at,
        "jti": token_id,
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return token, token_id, expires_at
