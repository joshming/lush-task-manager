from typing import List

from httpx import AsyncClient

PROJECT_QUERY = """
    query Project($project_id: Int!) {
        project(id_: $project_id) {
            id
            title
            description
        }
    }
"""

PROJECTS_QUERY = """
    query Project {
        projects {
            id
            title
            description
        }
    }
"""


class TestProjectQuery:

    async def test_get_project_by_id_exists_return_project(self, client: AsyncClient, project: int):
        response = await client.post("/tasks", json={
            "query": PROJECT_QUERY,
            "variables": {"project_id": project},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["project"]["id"] is not None
        assert data["data"]["project"]["title"] is not None

    async def test_get_tasks_none_inserted_return_empty_list(self, client: AsyncClient):
        response = await client.post("/tasks", json={
            "query": PROJECTS_QUERY,
            "variables": {},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["projects"] == []

    async def test_get_tasks_multiple_return_populated_list(self, client: AsyncClient, projects: List[int]):
        response = await client.post("/tasks", json={
            "query": PROJECTS_QUERY,
            "variables": {},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["projects"] != []