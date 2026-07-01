from typing import List

import strawberry
from strawberry import Info

from app.context import TaskManagementContext
from app.graphql.types.project import Project


@strawberry.type
class ProjectQuery:
    @strawberry.field
    async def project(self, id_: int, request: Info[TaskManagementContext, None]) -> Project:
        project_service = request.context.project_service

        return await project_service.get_project_by_id(id_)

    @strawberry.field
    async def projects(self, request: Info[TaskManagementContext, None]) -> List[Project]:
        project_service = request.context.project_service
        # TODO Paging, filterings sorting
        return await project_service.get_projects()