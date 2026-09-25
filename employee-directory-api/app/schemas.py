from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, ConfigDict

class EmployeeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=10)
    department: str = Field(min_length=2, max_length=100)
    designation: str = Field(min_length=2, max_length=100)


class EmployeeUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=10)
    department: str = Field(min_length=2, max_length=100)
    designation: str = Field(min_length=2, max_length=100)

class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: str
    department: str
    designation: str
    created_at: datetime
