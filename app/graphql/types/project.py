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
    created_date: datetime
    updated_date: datetime