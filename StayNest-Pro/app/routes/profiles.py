
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter(
    prefix="/api/v1/profiles",
    tags=["Profiles"],
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
