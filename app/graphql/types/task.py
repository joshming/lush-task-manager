from datetime import datetime

import strawberry

from app.enums import Priority as TaskPriority, TaskStatus

Status = strawberry.enum(TaskStatus)
Priority = strawberry.enum(TaskPriority)


@strawberry.type
class Task:
    id: int
    title: str
    description: str | None
    priority: Priority
    status: Status
    project_id: int
    assigned_to: int | None
    created_by: int
    created_at: datetime
    updated_at: datetime


@strawberry.input
class UpdateTaskInput:
    title: str | None = None
    description: str | None = None
    assigned_user: int | None = None
    priority: Priority | None = None
    status: Status | None = None
