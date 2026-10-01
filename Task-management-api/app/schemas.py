from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Status(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class TaskCreate(BaseModel):
    task_id: int
    task_title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: Priority
    status: Status
    due_date: date
    assigned_to: str = Field(min_length=1)


class TaskResponse(BaseModel):
    task_id: int
    task_title: str
    description: str
    priority: Priority
    status: Status
    due_date: date
    assigned_to: str
    created_date: datetime