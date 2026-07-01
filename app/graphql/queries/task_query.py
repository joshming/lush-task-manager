from typing import List

import strawberry
from strawberry.types import Info

from app.context import TaskManagementContext
from app.graphql.types.task import Task


@strawberry.type
class TaskQuery:
    @strawberry.field
    async def task(self, id_: int, request: Info[TaskManagementContext, None]) -> Task:
        task_service = request.context.task_service

        return await task_service.get_task_by_id(id_)

    @strawberry.field
    async def tasks(self, request: Info[TaskManagementContext, None]) -> List[Task]:
        task_service = request.context.task_service

        return await task_service.get_tasks()