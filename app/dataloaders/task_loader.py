from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from app.models.task import Task
from database import get_db


async def load_tasks_by_id(db: AsyncSession, keys: list[int]) -> list[Task | None]:
    result = await db.execute(
        select(Task).where(Task.id.in_(keys))
    )
    tasks = {task.id: task for task in result.scalars().all()}

    return [tasks.get(key) for key in keys]

def get_task_loader(db: AsyncSession = Depends(get_db)) -> DataLoader:
    return DataLoader(load_fn=lambda keys: load_tasks_by_id(db, keys))