from sqlalchemy.ext.asyncio import AsyncSession

from app import ProjectDAO, TaskDAO
from app.enums import TaskStatus
from app.graphql.types.task import Task
from app.schemas.task import CreateTask
from app.services.project_exception import ProjectNotFoundException


class TaskService:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_task_by_id(self, id_: int) -> Task | None:
        taskDAO = await self._db.get(TaskDAO, id_)

        if not taskDAO:
            return None

        return Task(
            id=taskDAO.id,
            title=taskDAO.title,
            description=taskDAO.description,
            priority=taskDAO.priority,
            status=taskDAO.status,
            project_id=taskDAO.project_id,
            assigned_to=taskDAO.assigned_to,
            created_at=taskDAO.created_at,
            updated_at=taskDAO.updated_at
        )

    async def create_task(self, user: int, task_request: CreateTask) -> Task:
        project = await self._db.get(ProjectDAO, task_request.project)
        if not project:
            raise ProjectNotFoundException("No project exists with")

        task_dao = TaskDAO(
            title=task_request.title,
            description=task_request.description,
            status=TaskStatus.TODO,
            priority=task_request.priority,
            project_id=task_request.project,
            created_by=user
        )

        self._db.add(task_dao)
        await self._db.commit()
        await self._db.refresh(task_dao)

        return Task(
            id=task_dao.id,
            title=task_dao.title,
            description=task_dao.description,
            priority=task_dao.priority,
            status=task_dao.status,
            project_id=task_dao.project_id,
            assigned_to=task_dao.assigned_to,
            created_at=task_dao.created_at,
            updated_at=task_dao.updated_at,
        )
