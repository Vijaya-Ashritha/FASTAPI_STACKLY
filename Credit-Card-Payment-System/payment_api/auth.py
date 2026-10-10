from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from rest_framework_simplejwt.tokens import (
    AccessToken,
)


security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
) -> int:

    try:

        token = AccessToken(
            credentials.credentials
        )

        user_id = token["user_id"]

        return int(user_id)

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid or expired access token."
            ),
        ) from exc