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


class TestTaskMutations:

    async def test_create_task_valid_input(self, client, project: int):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": "Test Task", "description": "A test task", "projectId": project},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["createTask"]["id"] is not None
        assert data["data"]["createTask"]["description"] == "A test task"

    async def test_create_task_no_project(self, client):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": "Test Task", "description": "A test task", "projectId": 1234567},
        })
        data = response.json()
        assert "errors" in data

    async def test_create_task_blank_title(self, client, project: int):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": "", "description": "A test task", "projectId": project},
        })
        data = response.json()
        assert "errors" in data

    async def test_create_task_null_title(self, client, project: int):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": None, "description": "A test task", "projectId": project},
        })
        data = response.json()
        assert "errors" in data

    async def test_create_task_null_description(self, client, project: int):
        response = await client.post("/tasks", json={
            "query": CREATE_TASK_MUTATION,
            "variables": {"title": "test task", "description": None, "projectId": project},
        })
        data = response.json()
        assert "errors" not in data
        assert data["data"]["createTask"]["description"] is None