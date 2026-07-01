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

UPDATE_PROJECT_MUTATION = """
    mutation UpdateProject($projectId: Int!, $title: String, $description: String) {
        updateProject(projectId: $projectId, projectInput: { title: $title, description: $description}) {
            id
            title
            description
        }
    }
"""

DELETE_PROJECT_MUTATION = """
    mutation DeleteProject($id: Int!) {
        deleteProject(projectId: $id) {
            id
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

    async def test_update_project_owned(self, client: AsyncClient, project: int):
        response = await client.post("/tasks", json={
            "query": UPDATE_PROJECT_MUTATION,
            "variables": {"projectId": project, "description": "updated project"}
        })

        data = response.json()
        assert "errors" not in data
        assert data["data"]["updateProject"]["id"] is not None

    async def test_update_project_unowned(self, client: AsyncClient, project: int):
        client.headers["X-User-Id"] = "2"
        response = await client.post("/tasks", json={
            "query": UPDATE_PROJECT_MUTATION,
            "variables": {"projectId": project, "description": "updated project"}
        })

        data = response.json()
        assert "errors" in data

    async def test_update_project_blank_title(self, client: AsyncClient, project: int):
        response = await client.post("/tasks", json={
            "query": UPDATE_PROJECT_MUTATION,
            "variables": {"projectId": project, "description": "updated project", "title": ""}
        })

        data = response.json()
        assert "errors" in data

    async def test_delete_project_owned(self, client: AsyncClient, project: int):
        response = await client.post("/tasks", json={
            "query": DELETE_PROJECT_MUTATION,
            "variables": {"id": project}
        })

        data = response.json()
        assert "errors" not in data

    async def test_delete_project_missing(self, client: AsyncClient):
        response = await client.post("/tasks", json={
            "query": DELETE_PROJECT_MUTATION,
            "variables": {"id": 1}
        })

        data = response.json()
        assert "errors" in data

    async def test_delete_project_unowned(self, client: AsyncClient, project: int):
        client.headers["X-User-Id"] = "2"
        response = await client.post("/tasks", json={
            "query": DELETE_PROJECT_MUTATION,
            "variables": {"id": project}
        })

        data = response.json()
        assert "errors" in data
