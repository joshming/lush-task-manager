from datetime import datetime

import strawberry

from app.enums import ProjectStatus

Status = strawberry.enum(ProjectStatus)


@strawberry.type
class Project:
    id: int
    title: str
    description: str | None
    status: Status
    created_by: int
    created_at: datetime
    updated_at: datetime


@strawberry.input
class UpdateProjectInput:
    title: str | None = None
    description: str | None = None
    status: Status | None = None
