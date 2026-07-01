from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import ProjectDAO, TaskDAO, User
from app.enums import TaskStatus
from app.graphql.types.task import Task
from app.schemas.task import CreateTask, UpdateTask
from app.services.entity_exceptions import ProjectNotFound, UserNotFound
from app.services.entity_exceptions import TaskNotFound


def create_task(task_dao: TaskDAO) -> Task:
    return Task(
        id=task_dao.id,
        title=task_dao.title,
        description=task_dao.description,
        priority=task_dao.priority,
        status=task_dao.status,
        project_id=task_dao.project_id,
        assigned_to=task_dao.assigned_to,
        created_at=task_dao.created_at,
        updated_at=task_dao.updated_at
    )


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TaskService:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_task_by_id(self, id_: int) -> Task:
        task_dao = await self._db.get(TaskDAO, id_)

        if not task_dao:
            raise TaskNotFound(f"No task exists with id {id_}")

        return create_task(task_dao)

    async def get_tasks(self) -> list[Task]:
        query = await self._db.execute(select(TaskDAO))

        task_daos = query.scalars()
        if not task_daos:
            return []

        return [create_task(task_dao) for task_dao in task_daos]

    async def create_task(self, user: int, task_request: CreateTask) -> Task:
        project = await self._db.get(ProjectDAO, task_request.project)
        if not project:
            raise ProjectNotFound(f"No project exists with {task_request.project}")

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

        return create_task(task_dao)

    async def update_task(self, task_id: int, task_request: UpdateTask) -> Task:
        task_dao = await self._db.get(TaskDAO, task_id)

        if not task_dao:
            raise TaskNotFound(f"No task exists with id {task_id}")

        if task_request.title:
            task_dao.title = task_request.title

        if task_request.description:
            task_dao.description = task_request.description

        if task_request.priority:
            task_dao.priority = task_request.priority

        if task_request.status:
            task_dao.status = task_request.status

        if task_request.assigned_user:
            user_dao = await self._db.get(User, task_request.assigned_user)
            if not user_dao:
                raise UserNotFound(f"No user exists with id {task_request.assigned_user}")
            task_dao.assigned_to = task_request.assigned_user

        task_dao.updated_at = now_utc()
        await self._db.commit()
        await self._db.refresh(task_dao)

        return create_task(task_dao)