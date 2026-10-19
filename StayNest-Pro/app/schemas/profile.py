
from pydantic import BaseModel, EmailStr


class ProfileResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    email_verified: bool

    model_config = {"from_attributes": True}
