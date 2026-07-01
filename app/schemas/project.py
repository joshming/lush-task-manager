from typing import Annotated

from pydantic import BaseModel, StringConstraints


class CreateProject(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    description: str | None
