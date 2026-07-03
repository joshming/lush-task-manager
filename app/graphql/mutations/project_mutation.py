import strawberry
from strawberry.field_extensions import InputMutationExtension
from strawberry.types import Info

from app.context import TaskManagementContext
from app.graphql.types.project import Project, UpdateProjectInput
from app.schemas.project import CreateProject, UpdateProject


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

    @strawberry.mutation
    async def update_project(self,
                             request: Info[TaskManagementContext, None],
                             project_id: int,
                             project_input: UpdateProjectInput) -> Project:
        validated_update = UpdateProject(
            title=project_input.title,
            description=project_input.description,
            status=project_input.status
        )
        user_id = request.context.current_user
        project_service = request.context.project_service
        return await project_service.update_project(project_id, user_id, validated_update)

    @strawberry.mutation
    async def delete_project(self, request: Info[TaskManagementContext, None], project_id: int) -> Project:
        user_id = request.context.current_user
        project_service = request.context.project_service
        return await project_service.delete_project(project_id, user_id)
