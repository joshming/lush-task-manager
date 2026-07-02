from typing import List, Dict

from httpx import AsyncClient

TASK_QUERY = """
    query Task($task_id: Int!) {
        task(id_: $task_id) {
            id
            title
            description
            priority
            status
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
            assignedTo
            createdAt
            updatedAt
        }
    }
"""

TASKS_QUERY_WITH_PROJECTS = """
    query Task {
        tasks {
            id
            title
            description
            priority
            status
            assignedTo
            createdAt
            updatedAt
            project {
                id, 
                title
            }
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

    async def test_get_tasks_batched_projects(self, client: AsyncClient, tasks: List[int], query_counter: Dict[str, int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY_WITH_PROJECTS,
            "variables": {},
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        assert query_counter["queries"] == 2

    async def test_get_tasks_no_projects(self, client: AsyncClient, tasks: List[int], query_counter: Dict[str, int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY,
            "variables": {},
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        assert query_counter["queries"] == 1