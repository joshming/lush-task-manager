from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from app import ProjectDAO
from database import get_db


async def load_projects_by_id(db: AsyncSession, keys: List[int]) -> List[ProjectDAO | None]:
    result = await db.execute(
        select(ProjectDAO).where(ProjectDAO.id.in_(keys))
    )
    tasks = {task.id: task for task in result.scalars().all()}

    return [tasks.get(key) for key in keys]


def get_project_loader(db: AsyncSession = Depends(get_db)) -> DataLoader:
    return DataLoader(
        load_fn=lambda keys: load_projects_by_id(db, keys)
    )