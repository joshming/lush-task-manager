from datetime import datetime

import strawberry
from strawberry import Info

from app.enums import Priority as TaskPriority, TaskStatus
from app.graphql.types.project import Project

Status = strawberry.enum(TaskStatus)
Priority = strawberry.enum(TaskPriority)


@strawberry.type
class Task:
    id: int
    title: str
    description: str | None
    priority: Priority
    status: Status
    project_id: strawberry.Private[int]
    assigned_to: int | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def project(self, request: Info) -> Project:
        return await request.context.project_loader.load(self.project_id)

@strawberry.input
class UpdateTaskInput:
    title: str | None = None
    description: str | None = None
    assigned_user: int | None = None
    priority: Priority | None = None
    status: Status | None = None


@strawberry.input
class TaskFilterInput:
    project_id: int | None = None
    assigned_to: int | None = None
    status: Status | None = None
    priority: Priority | None = None
