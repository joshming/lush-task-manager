from typing import List

from httpx import AsyncClient

TASK_QUERY = """
    query Task($task_id: Int!) {
        task(id_: $task_id) {
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

TASKS_QUERY = """
    query Task {
        tasks {
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


class TestTaskQuery:

    async def test_get_task_by_id_exists(self, client: AsyncClient, task: int):
        response = await client.post("/tasks", json={
            "query": TASK_QUERY,
            "variables": {"task_id": task},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["task"]["id"] is not None
        assert data["data"]["task"]["title"] is not None

    async def test_get_tasks_none_inserted(self, client: AsyncClient):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY,
            "variables": {},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] == []

    async def test_get_tasks_multiple(self, client: AsyncClient, tasks: List[int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY,
            "variables": {},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []