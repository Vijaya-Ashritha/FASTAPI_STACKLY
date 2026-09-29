
from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    student_id: int
    student_name: str
    email: EmailStr
    phone: str | None = Field(default=None, pattern=r"^\d{10}$")
    age: int = Field(ge=18, le=60)
    course: str
    address: str | None = None


class StudentResponse(BaseModel):
    student_id: int
    student_name: str
    email: EmailStr
    phone: str | None = None
    age: int
    course: str
    address: str | None = None
