from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.enums import Priority


class CreateTask(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    description: str | None
    project: int
    priority: Priority | None