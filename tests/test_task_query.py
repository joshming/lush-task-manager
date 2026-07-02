from typing import List, Dict

from httpx import AsyncClient

from app.enums import TaskSortOption, SortDirection, Priority

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

TASKS_QUERY_WITH_FILTER = """
    query Task($project_id: Int, $assigned_to: Int, $status: TaskStatus, $priority: Priority) {
        tasks(filterInput: { projectId: $project_id, assignedTo: $assigned_to, status: $status, priority: $priority }) {
            id
            title
            status, 
            priority, 
            assignedTo,
            project {
                id, 
                title
            }
        }
    }
"""

TASKS_QUERY_WITH_SORT = """
    query Task($sort: TaskSortOption, $direction: SortDirection) {
        tasks(sort: { sort: $sort, direction: $direction }) {
            id
            title
            status, 
            priority, 
            assignedTo,
            project {
                id, 
                title
            }
        }
    }
"""


class TestTaskQuery:

    async def test_get_task_by_id_exists_returns_task(self, client: AsyncClient, task: int):
        response = await client.post("/tasks", json={
            "query": TASK_QUERY,
            "variables": {"task_id": task},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["task"]["id"] is not None
        assert data["data"]["task"]["title"] is not None

    async def test_get_tasks_none_inserted_returns_empty(self, client: AsyncClient):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY,
            "variables": {},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] == []

    async def test_get_tasks_multiple_returns_full_list(self, client: AsyncClient, tasks: List[int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY,
            "variables": {},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

    async def test_get_tasks_batched_projects_then_execute_two_queries(self, client: AsyncClient, tasks: List[int], query_counter: Dict[str, int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY_WITH_PROJECTS,
            "variables": {},
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        assert query_counter["queries"] == 2

    async def test_get_tasks_no_projects_then_execute_single_query(self, client: AsyncClient, tasks: List[int], query_counter: Dict[str, int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY,
            "variables": {},
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        assert query_counter["queries"] == 1

    async def test_get_tasks_project_filter_return_project_1_tasks(self, client: AsyncClient, tasks: List[int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY_WITH_FILTER,
            "variables": { "project_id": 1 },
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        tasks = data["data"]["tasks"]
        for task in tasks:
            assert task["project"]["id"] == 1

    async def test_get_tasks_assignee_filter_return_assignee_tasks(self, client: AsyncClient, tasks: List[int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY_WITH_FILTER,
            "variables": { "assigned_to": 1 },
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        tasks = data["data"]["tasks"]
        for task in tasks:
            assert task["assignedTo"] == 1

    async def test_get_tasks_sorted_id_descending_then_descending_id(self,client: AsyncClient, tasks: List[int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY_WITH_SORT,
            "variables": {"sort": TaskSortOption.ID, "direction": SortDirection.DESCENDING },
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        tasks = data["data"]["tasks"]
        last = len(tasks) + 1
        for task in tasks:
            assert task["id"] <= last
            last = task["id"]

    async def test_get_tasks_sorted_id_ascending_then_ascending_id(self,client: AsyncClient, tasks: List[int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY_WITH_SORT,
            "variables": {"sort": TaskSortOption.ID, "direction": SortDirection.ASCENDING },
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        tasks = data["data"]["tasks"]
        last = -1
        for task in tasks:
            assert task["id"] >= last
            last = task["id"]

    async def test_get_tasks_sorted_nullable_descending_then_nulls_first(self,client: AsyncClient, some_assigned_tasks: List[int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY_WITH_SORT,
            "variables": {"sort": TaskSortOption.USER, "direction": SortDirection.DESCENDING },
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        tasks = data["data"]["tasks"]
        last = None
        for task in tasks:
            assert (task["assignedTo"] is None and last is None) or (last is None or task["assignedTo"] < last)
            last = task["assignedTo"]

    async def test_get_tasks_sorted_priority_descending_then_high_first(self,client: AsyncClient, tasks: List[int]):
        response = await client.post("/tasks", json={
            "query": TASKS_QUERY_WITH_SORT,
            "variables": {"sort": TaskSortOption.PRIORITY, "direction": SortDirection.DESCENDING },
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["tasks"] != []

        tasks = data["data"]["tasks"]
        last = None
        assert tasks[0]["priority"] == "HIGH"
        assert tasks[1]["priority"] == "MEDIUM"
        assert tasks[2]["priority"] == "MEDIUM"
        assert tasks[3]["priority"] == "MEDIUM"
