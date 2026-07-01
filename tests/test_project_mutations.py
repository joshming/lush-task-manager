from httpx import AsyncClient

CREATE_PROJECT_MUTATION = """
    mutation CreateProject($title: String!, $description: String) {
        createProject(input: {title: $title, description: $description}) {
            id
            title
            description
        }
    }
"""

class TestProjectMutations:

    async def test_create_project_valid_input(self, client: AsyncClient):
        response = await client.post("/tasks", json={
            "query": CREATE_PROJECT_MUTATION,
            "variables": {"title": "Test Project", "description": "A test project"}
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["createProject"]["id"] is not None

    async def test_create_project_missing_title(self, client: AsyncClient):
        response = await client.post("/tasks", json={
            "query": CREATE_PROJECT_MUTATION,
            "variables": {"title": "", "description": "A test project"}
        })
        data = response.json()
        assert "errors" in data