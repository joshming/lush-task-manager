import strawberry
from strawberry.field_extensions import InputMutationExtension
from strawberry.types import Info

from app.context import TaskManagementContext
from app.enums import Priority
from app.graphql.types.task import Task, UpdateTaskInput
from app.schemas.task import CreateTask, UpdateTask


@strawberry.type
class TaskMutation:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def create_task(self,
                          request: Info[TaskManagementContext, None],
                          title: str,
                          project_id: int,
                          description: str | None = None,
                          priority: Priority | None = Priority.MEDIUM) -> Task:
        validated_creation = CreateTask(
            title=title,
            description=description,
            project=project_id,
            priority=priority,
        )  # TODO pydantic exception handling

        task_service = request.context.task_service
        user_id = request.context.current_user
        return await task_service.create_task(user_id, validated_creation)

    @strawberry.mutation
    async def update_task(self,
                          request: Info[TaskManagementContext, None],
                          task_id: int,
                          update_input: UpdateTaskInput) -> Task:
        update_request = UpdateTask(
            title=update_input.title,
            description=update_input.description,
            assigned_user=update_input.assigned_user,
            priority=update_input.priority,
            status=update_input.status,
        )

        task_service = request.context.task_service
        return await task_service.update_task(task_id, update_request)