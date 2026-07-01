import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import BigInteger

from app import Base
from app.main import app, get_current_user
from database import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@compiles(BigInteger, "sqlite")
def compile_big_int_sqlite(type_, compiler, **kw):
    """Force SQLite to see BigInteger as Integer to enable autoincrement."""
    return "INTEGER"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with TestSession() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    # Override get_db to use test session
    async def override_get_db():
        yield db_session

    # Override auth to return a stub user
    async def override_get_current_user():
        return 1

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
async def project(client):
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
async def task(client, project: int):
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
