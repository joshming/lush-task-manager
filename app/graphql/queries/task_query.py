from typing import List

import strawberry
from strawberry.types import Info

from app.context import TaskManagementContext
from app.enums import TaskSortOption
from app.graphql.types.task import Task, TaskFilterInput, TaskSortInput
from app.schemas.task import TaskFilter, TaskSort


@strawberry.type
class TaskQuery:
    @strawberry.field
    async def task(self, id_: int, request: Info[TaskManagementContext, None]) -> Task:
        task_service = request.context.task_service

        return await task_service.get_task_by_id(id_)

    @strawberry.field
    async def tasks(self, request: Info[TaskManagementContext, None], sort: TaskSortInput | None = None, filter_input: TaskFilterInput | None = None) -> List[Task]:
        task_service = request.context.task_service
        task_filter = None
        if filter_input:
            task_filter = TaskFilter(
                project_id=filter_input.project_id,
                assigned_to=filter_input.assigned_to,
                status=filter_input.status,
                priority=filter_input.priority
            )

        task_sort = None
        if sort:
            task_sort = TaskSort(
                sort_by=sort.sort,
                order=sort.direction
            )

        return await task_service.get_tasks(task_filter, task_sort)