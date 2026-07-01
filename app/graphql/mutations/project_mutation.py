import strawberry
from strawberry.field_extensions import InputMutationExtension
from strawberry.types import Info

from app.context import TaskManagementContext
from app.graphql.types.project import Project
from app.schemas.project import CreateProject


@strawberry.type
class ProjectMutation:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def create_project(self,
                             request: Info[TaskManagementContext, None],
                             title: str,
                             description: str | None=None) -> Project:
        project_request = CreateProject(title=title, description=description)

        user_id = request.context.current_user
        project_service = request.context.project_service

        return await project_service.create_project(user_id, project_request)
