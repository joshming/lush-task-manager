from typing import List, Any, AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import variables
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import BigInteger

from app import Base, User
from app.main import app, get_current_user
from database import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@compiles(BigInteger, "sqlite")
def compile_big_int_sqlite(type_, compiler, **kw):
    """Force SQLite to see BigInteger as Integer to enable autoincrement."""
    return "INTEGER"


@pytest_asyncio.fixture
async def engine() -> AsyncEngine:
    return create_async_engine(TEST_DATABASE_URL, echo=False)


@pytest_asyncio.fixture
async def get_async_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine, get_async_session_maker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[
    Any, Any]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as client:
        client.headers.__setitem__("X-User-Id", "1")
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def users(db_session: AsyncSession) -> List[int]:
    users = [
        User(first_name="John", last_name="Smith"),
        User(first_name="Jane", last_name="Doe")
    ]

    db_session.add_all(users)
    await db_session.commit()
    return [user.id for user in users]


@pytest.fixture
async def project(client: AsyncClient) -> int:
    project = await client.post("/tasks", json={
        "query": """
            mutation {
                createProject(input: { title: "Test Project" }) {
                    id
                }
            }
        """
    })
    return project.json()["data"]["createProject"]["id"]


@pytest.fixture
async def projects(client: AsyncClient) -> List[int]:
    p1 = await client.post("/tasks", json={
        "query": """
            mutation {
                createProject(input: { title: "Test Project 1" }) {
                    id
                }
            }
        """
    })

    p2 = await client.post("/tasks", json={
        "query": """
            mutation {
                createProject(input: { title: "Test Project 2" }) {
                    id
                }
            }
        """
    })

    p3 = await client.post("/tasks", json={
        "query": """
            mutation {
                createProject(input: { title: "Test Project 3" }) {
                    id
                }
            }
        """
    })

    return [p1.json()["data"]["createProject"]["id"], p2.json()["data"]["createProject"]["id"],
            p3.json()["data"]["createProject"]["id"]]


@pytest.fixture
async def task(client: AsyncClient, project: int) -> int:
    task = await client.post("/tasks", json={
        "query": """
            mutation {
                createTask(input: { title: "test task", projectId: 1 }) {
                    id
                }
            }
        """
    })

    return task.json()["data"]["createTask"]["id"]


@pytest.fixture
async def tasks(client: AsyncClient, projects: List[int], users: List[int]) -> List[int]:
    t1 = await client.post("/tasks", json={
        "query": """
                mutation {
                    createTask(input: { title: "test task 1", projectId: 1 }) {
                        id
                    }
                }
            """
    })

    t2 = await client.post("/tasks", json={
        "query": """
                mutation {
                    createTask(input: { title: "test task 2", projectId: 2 }) {
                        id
                    }
                }
            """
    })

    t3 = await client.post("/tasks", json={
        "query": """
                mutation {
                    createTask(input: { title: "test task 3", projectId: 3 }) {
                        id
                    }
                }
            """
    })

    tasks = [
        t1.json()["data"]["createTask"]["id"],
        t2.json()["data"]["createTask"]["id"],
        t3.json()["data"]["createTask"]["id"],
    ]

    for task in tasks:
        assigned_task = await client.post("/tasks", json={
            "query": """
                mutation UpdateTask($task_id: Int!, $assignedUser: Int!) {
                    updateTask(taskId: $task_id, updateInput: { assignedUser: $assignedUser }) {
                        id,
                        assignedTo
                    }
                }
            """,
            "variables": {"task_id": task, "assignedUser": 1}
        })

        assigned_task.json()["data"]["updateTask"]["id"]

    return tasks


@pytest.fixture
def query_counter(engine: AsyncEngine):
    count = {"queries": 0}

    def before_cursor_execute(
            conn,
            cursor,
            statement,
            parameters,
            context,
            executemany,
    ):
        count["queries"] += 1

    event.listen(engine.sync_engine, "before_cursor_execute", before_cursor_execute)

    yield count

    event.remove(engine.sync_engine, "before_cursor_execute", before_cursor_execute)
