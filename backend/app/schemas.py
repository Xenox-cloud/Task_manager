from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import Priority, TaskStatus


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    status: TaskStatus = TaskStatus.todo
    priority: Priority = Priority.medium
    due_date: date | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    """All fields optional so the client can send a partial update (PATCH)."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: Priority | None = None
    due_date: date | None = None


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class TaskStats(BaseModel):
    total: int
    by_status: dict[str, int]
    overdue: int
