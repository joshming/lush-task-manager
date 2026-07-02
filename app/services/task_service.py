from datetime import datetime, timezone
from typing import Any

from asyncpg import ForeignKeyViolationError, UniqueViolationError
from sqlalchemy import select, Select, case, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from app import TaskDAO, User
from app.enums import TaskStatus, TaskSortOption, SortDirection
from app.graphql.types.task import Task
from app.schemas.task import CreateTask, UpdateTask, TaskFilter, TaskSort
from app.services.entity_exceptions import ProjectNotFound, UserNotFound, UnauthorizedTaskException, \
    DuplicateTaskException, RefreshException
from app.services.entity_exceptions import TaskNotFound

PRIORITY_ORDER = case(
    {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    },
    value=TaskDAO.priority
)

STATUS_ORDER = case(
    {
        "TODO": 1,
        "PROGRESS": 2,
        "CLOSED": 3,
    },
    value=TaskDAO.status
)


def create_task(task_dao: TaskDAO) -> Task:
    return Task(
        id=task_dao.id,
        title=task_dao.title,
        description=task_dao.description,
        priority=task_dao.priority,
        status=task_dao.status,
        project_id=task_dao.project_id,
        assigned_to=task_dao.assigned_to,
        created_by=task_dao.created_by,
        created_at=task_dao.created_at,
        updated_at=task_dao.updated_at
    )


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def apply_filters(task_filter: TaskFilter | None, sort: TaskSort | None) -> Select[tuple[Any]]:
    if not task_filter and not sort:
        return select(TaskDAO)

    query = select(TaskDAO)

    conditions = []
    if task_filter:
        if task_filter.project_id is not None:
            conditions.append(TaskDAO.project_id == task_filter.project_id)

        if task_filter.assigned_to is not None:
            conditions.append(TaskDAO.assigned_to == task_filter.assigned_to)

        if task_filter.status is not None:
            conditions.append(TaskDAO.status == task_filter.status)

        if task_filter.priority is not None:
            conditions.append(TaskDAO.priority == task_filter.priority)

    if not sort or not sort.sort_by:
        return query.where(*conditions)

    direction = SortDirection.ASCENDING if not sort.order else sort.order
    match sort.sort_by:
        case TaskSortOption.PRIORITY:
            return query.where(*conditions).order_by(asc(PRIORITY_ORDER) if direction == SortDirection.ASCENDING else desc(PRIORITY_ORDER))
        case TaskSortOption.STATUS:
            return query.where(*conditions).order_by(asc(STATUS_ORDER) if direction == SortDirection.ASCENDING else desc(STATUS_ORDER))
        case TaskSortOption.ID:
            return query.where(*conditions).order_by(asc(TaskDAO.id) if direction == SortDirection.ASCENDING else desc(TaskDAO.id))
        case TaskSortOption.USER:
            return query.where(*conditions).order_by(asc(TaskDAO.assigned_to).nullslast() if direction == SortDirection.ASCENDING else desc(TaskDAO.assigned_to).nullsfirst())
        case TaskSortOption.PROJECT_ID:
            return query.where(*conditions).order_by(asc(TaskDAO.project_id) if direction == SortDirection.ASCENDING else desc(TaskDAO.project_id))
        case _:
            return query.where(*conditions)


class TaskService:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_task_by_id(self, id_: int) -> Task:
        task_dao = await self._db.get(TaskDAO, id_)

        if not task_dao:
            raise TaskNotFound(f"No task exists with id {id_}")

        return create_task(task_dao)

    async def get_tasks(self, task_filter: TaskFilter | None, sort: TaskSort | None) -> list[Task]:
        query = apply_filters(task_filter, sort)

        result = await self._db.execute(query)

        task_daos = result.scalars()
        if not task_daos:
            return []

        return [create_task(task_dao) for task_dao in task_daos]

    async def create_task(self, user: int, task_request: CreateTask) -> Task:
        task_dao = TaskDAO(
            title=task_request.title,
            description=task_request.description,
            status=TaskStatus.TODO,
            priority=task_request.priority,
            project_id=task_request.project,
            created_by=user,
            normalized_title=task_request.title.lower().strip()
        )

        try:
            self._db.add(task_dao)
            await self._db.commit()
        except IntegrityError as e:
            await self._db.rollback()
            original = e.orig.__cause__ if e.orig else None
            print(f"original error {type(original)}")
            if isinstance(original, ForeignKeyViolationError):
                raise ProjectNotFound(f"No project exists with {task_request.project}")
            elif isinstance(original, UniqueViolationError):
                raise DuplicateTaskException(f"A task with title {task_request.title} already exists")
            raise e

        await self._db.refresh(task_dao)

        return create_task(task_dao)

    async def update_task(self, task_id: int, task_request: UpdateTask) -> Task:
        task_dao = await self._db.get(TaskDAO, task_id)

        if not task_dao:
            raise TaskNotFound(f"No task exists with id {task_id}")

        if task_request.title:
            task_dao.title = task_request.title
            task_dao.normalized_title = task_request.title.lower().strip()

        if task_request.description:
            task_dao.description = task_request.description

        if task_request.priority:
            task_dao.priority = task_request.priority

        if task_request.status:
            task_dao.status = task_request.status

        if task_request.assigned_user:
            task_dao.assigned_to = task_request.assigned_user

        task_dao.updated_at = now_utc()
        try:
            await self._db.commit()
        except IntegrityError as e:
            await self._db.rollback()
            original = e.orig.__cause__ if e.orig else None

            if isinstance(original, ForeignKeyViolationError):
                raise UserNotFound(f"No user exists with id {task_request.assigned_user}")
            elif isinstance(original, UniqueViolationError):
                raise DuplicateTaskException(f"A task with title {task_request.title} already exists")
            raise e
        except StaleDataError:
            await self._db.rollback()
            raise RefreshException(f"Please refresh, task {task_dao.title} has been edited already.")

        await self._db.refresh(task_dao)

        return create_task(task_dao)

    async def delete_task(self, task_id: int, user_id: int) -> Task:
        task_dao = await self._db.get(TaskDAO, task_id)

        if not task_dao:
            raise TaskNotFound(f"No task exists with id {task_id}")

        if task_dao.created_by != user_id:
            raise UnauthorizedTaskException(f"You cannot delete the task")

        await self._db.delete(task_dao)
        await self._db.commit()

        return create_task(task_dao)
