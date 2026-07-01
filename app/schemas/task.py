from typing import Annotated

from pydantic import BaseModel, StringConstraints, field_validator

from app.enums import Priority, TaskStatus


class CreateTask(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    description: str | None
    project: int
    priority: Priority | None


class UpdateTask(BaseModel):
    title: str | None
    assigned_user: int | None
    description: str | None
    priority: Priority | None
    status: TaskStatus | None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("title cannot be empty")
        return v
