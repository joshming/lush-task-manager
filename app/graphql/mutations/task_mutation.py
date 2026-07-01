import strawberry
from strawberry.field_extensions import InputMutationExtension
from strawberry.types import Info

from app.context import TaskManagementContext
from app.enums import Priority
from app.graphql.types.task import Task
from app.schemas.task import CreateTask


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
        ) # TODO pydantic exception handling

        task_service = request.context.task_service
        user_id = request.context.current_user
        return await task_service.create_task(user_id, validated_creation)

