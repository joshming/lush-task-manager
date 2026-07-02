from typing import List

import strawberry
from strawberry.types import Info

from app.context import TaskManagementContext
from app.graphql.types.task import Task, TaskFilterInput
from app.schemas.task import TaskFilter


@strawberry.type
class TaskQuery:
    @strawberry.field
    async def task(self, id_: int, request: Info[TaskManagementContext, None]) -> Task:
        task_service = request.context.task_service

        return await task_service.get_task_by_id(id_)

    @strawberry.field
    async def tasks(self, request: Info[TaskManagementContext, None], filter_input: TaskFilterInput | None = None) -> List[Task]:
        task_service = request.context.task_service

        if not filter_input:
            return await task_service.get_tasks(None)

        task_filter = TaskFilter(
            project_id=filter_input.project_id,
            assigned_to=filter_input.assigned_to,
            status=filter_input.status,
            priority=filter_input.priority
        )

        return await task_service.get_tasks(task_filter)