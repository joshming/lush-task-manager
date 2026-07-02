from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext

from app.services.project_service import ProjectService
from app.services.task_service import TaskService


class TaskManagementContext(BaseContext):
    current_user: int
    task_service: TaskService
    project_service: ProjectService
    project_loader: DataLoader

    def __init__(self,
                 current_user: int,
                 task_service: TaskService,
                 project_service: ProjectService,
                 project_loader: DataLoader) -> None:
        super().__init__()
        self.current_user = current_user
        self.task_service = task_service
        self.project_service = project_service
        self.project_loader = project_loader
