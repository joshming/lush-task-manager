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
    created_at: datetime
    updated_at: datetime