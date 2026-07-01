from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from app import TaskDAO

CREATE_TASK_MUTATION = """
    mutation CreateTask($title: String!, $description: String, $projectId: Int!) {
        createTask(
            input: { title: $title, description: $description, projectId: $projectId }
        ) {
            id
            title
            description
            priority
            status
            projectId
            assignedTo
            createdAt
            updatedAt
        }
    }
"""

UPDATE_TASK_MUTATION = """
    mutation UpdateTask($taskId: Int!, $description: String!) {
        updateTask(
            taskId: $taskId,
            updateInput: { description: $description}
        ) {
            id
            title
            description
            updatedAt
        }
    }
"""


class TestTaskMutations:

    async def test_create_task_valid_input(self, client: AsyncClient, project: int):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": "Test Task", "description": "A test task", "projectId": project},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["createTask"]["id"] is not None
        assert data["data"]["createTask"]["description"] == "A test task"

    async def test_create_task_no_project(self, client: AsyncClient):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": "Test Task", "description": "A test task", "projectId": 1234567},
        })
        data = response.json()
        assert "errors" in data

    async def test_create_task_blank_title(self, client: AsyncClient, project: int):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": "", "description": "A test task", "projectId": project},
        })
        data = response.json()
        assert "errors" in data

    async def test_create_task_null_title(self, client: AsyncClient, project: int):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": None, "description": "A test task", "projectId": project},
        })
        data = response.json()
        assert "errors" in data

    async def test_create_task_null_description(self, client: AsyncClient, project: int):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": "test task", "description": None, "projectId": project},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["createTask"]["description"] is None

    async def test_update_task_stale_data(self, get_async_session_maker: async_sessionmaker[AsyncSession], task: int):
        async with get_async_session_maker() as session:
            async with get_async_session_maker() as session2:
                task1 = await session.get(TaskDAO, task)
                task2 = await session2.get(TaskDAO, task)

                task1.description = "Updated description"
                await session.commit()
                try:
                    task2.description = "Updated description"
                    await session2.commit()
                except Exception as e:
                    assert type(e) is StaleDataError
