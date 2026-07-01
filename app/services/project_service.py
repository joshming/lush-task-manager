from sqlalchemy.ext.asyncio import AsyncSession

from app import ProjectDAO
from app.enums import ProjectStatus
from app.graphql.types.project import Project
from app.schemas.project import CreateProject


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
        return Project(
            id=project_dao.id,
            title=project_dao.title,
            description=project_dao.description,
            status=project_dao.status,
            created_by=project_dao.created_by,
            created_date=project_dao.created_at,
            updated_date=project_dao.updated_at
        )