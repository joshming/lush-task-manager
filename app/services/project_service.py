from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import ProjectDAO
from app.enums import ProjectStatus
from app.graphql.types.project import Project
from app.schemas.project import CreateProject, UpdateProject
from app.services.entity_exceptions import ProjectNotFound, UnauthorizedProjectException


def create_project(project_dao: ProjectDAO) -> Project:
    return Project(
        id=project_dao.id,
        title=project_dao.title,
        description=project_dao.description,
        status=project_dao.status,
        created_by=project_dao.created_by,
        created_date=project_dao.created_at,
        updated_date=project_dao.updated_at
    )

class ProjectService:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create_project(self, user_id: int, project_request: CreateProject) -> Project:
        project_dao = ProjectDAO(
            title=project_request.title,
            description=project_request.description,
            created_by=user_id,
            status=ProjectStatus.OPEN,
        )

        self._db.add(project_dao)
        await self._db.commit()
        await self._db.refresh(project_dao)
        return create_project(project_dao)

    async def update_project(self, project_id: int, user_id: int, update_project: UpdateProject) -> Project:
        project_dao = await self._db.get(ProjectDAO, project_id)

        if not project_dao:
            raise ProjectNotFound(f"Project with id {project_id} was not found.")

        if user_id != project_dao.created_by:
            raise UnauthorizedProjectException("You cannot edit this project")

        if update_project.title:
            project_dao.title = update_project.title

        if update_project.description:
            project_dao.description = update_project.description

        if update_project.status:
            project_dao.status = update_project.status

        await self._db.commit()
        await self._db.refresh(project_dao)
        return create_project(project_dao)

    async def delete_project(self, project_id: int, user_id: int) -> Project:
        project_dao = await self._db.get(ProjectDAO, project_id)

        if not project_dao:
            raise ProjectNotFound(f"Project with id {project_id} was not found.")

        if user_id != project_dao.created_by:
            raise UnauthorizedProjectException("You cannot delete this project")

        await self._db.delete(project_dao)
        await self._db.commit()
        return create_project(project_dao)

    async def get_project_by_id(self, project_id: int) -> Project:
        project_dao = await self._db.get(ProjectDAO, project_id)

        if not project_dao:
            raise ProjectNotFound(f"Project with id {project_id} was not found.")
        return create_project(project_dao)

    async def get_projects(self) -> List[Project]:
        results = await self._db.execute(
            select(ProjectDAO)
        )

        # TODO Figure out difference between results.scalars and results.all
        project_daos = results.scalars()
        if not project_daos:
            return []

        return [create_project(project_dao) for project_dao in project_daos]