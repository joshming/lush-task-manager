import strawberry
from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from strawberry.dataloader import DataLoader
from strawberry.fastapi import GraphQLRouter

from app.context import TaskManagementContext
from app.dataloaders.project_loader import get_project_loader
from app.dataloaders.task_loader import get_task_loader
from app.graphql.schemas import Query, Mutation
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from database import get_db


async def get_current_user(request: Request) -> int:
    """
    In an ideal world, a user principal would be retrieved from the auth header instead, and then validated.
    """
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return int(user_id)


async def get_task_service(db: AsyncSession = Depends(get_db)):
    return TaskService(db)


async def get_project_service(db: AsyncSession = Depends(get_db)):
    return ProjectService(db)


async def get_task_management_context(current_user: int = Depends(get_current_user),
                                      task_service: TaskService = Depends(get_task_service),
                                      project_service: ProjectService = Depends(get_project_service),
                                      task_loader: DataLoader = Depends(get_task_loader),
                                      project_loader: DataLoader = Depends(get_project_loader)):
    return TaskManagementContext(current_user, task_service, project_service, task_loader, project_loader)


schema = strawberry.Schema(query=Query, mutation=Mutation)

task_management = GraphQLRouter(schema=schema, context_getter=get_task_management_context)

app = FastAPI()
app.include_router(task_management, prefix="/tasks")
