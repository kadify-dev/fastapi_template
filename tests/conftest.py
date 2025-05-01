import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql import text

from app.core.config import settings
from app.db.database import Base
from app.main import app
from app.utils.unitofwork import UnitOfWork


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
    yield engine
    engine.sync_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(engine):
    async with engine.connect() as connection:
        async with AsyncSession(connection) as session:
            yield session


@pytest.fixture
async def client(session):
    async with session.begin():
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))

    class TestUnitOfWork(UnitOfWork):
        def __init__(self):
            self.session_factory = lambda: session

    app.dependency_overrides[UnitOfWork] = TestUnitOfWork

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=30.0
    ) as client:
        yield client

    app.dependency_overrides.clear()
