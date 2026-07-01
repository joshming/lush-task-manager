from typing import Annotated

from pydantic import BaseModel, StringConstraints, field_validator

from app.enums import ProjectStatus


class CreateProject(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    description: str | None

class UpdateProject(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("title cannot be empty")
        return v