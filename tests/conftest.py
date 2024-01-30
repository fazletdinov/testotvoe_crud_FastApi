from typing import Any, AsyncGenerator
from asyncio import current_task
import asyncio
from httpx import AsyncClient

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

from main import app
from src.core.config import get_settings
from src.database.models import Base
from src.database.session import db_helper

async_engine = create_async_engine(
    url=get_settings().db_test.async_url, echo=False, poolclass=StaticPool
)
async_session_factory = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

Base.metadata.bind = async_engine


def get_scoped_session() -> Any:
    session = async_scoped_session(
        session_factory=async_session_factory, scopefunc=current_task
    )
    return session


async def override_scoped_session_dependency() -> AsyncSession:
    session = get_scoped_session()
    yield session
    await session.close()


app.dependency_overrides[
    db_helper.scoped_session_dependency
] = override_scoped_session_dependency


@pytest.fixture(autouse=True, scope="class")
async def async_db_engine() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app,
        base_url=f"{get_settings().db_test.API_V1_STR}/api/v1",
        follow_redirects=True,
    ) as aclient:
        yield aclient


@pytest.fixture(scope="session")
async def db() -> AsyncGenerator[AsyncSession, None]:
    session = get_scoped_session()
    yield session
    await session.close()


@pytest.fixture
async def menu_data():
    return {
        "title": "title menu 1",
        "description": "description menu description 1",
    }


@pytest.fixture
async def submenu_data():
    return {
        "title": "title submenu 1",
        "description": "description submenu description 1",
    }


@pytest.fixture
async def dish_data():
    return {
        "title": "title dish 1",
        "description": "description dish description 1",
        "price": "77.77",
    }


@pytest.fixture
async def update_menu_data():
    return {
        "title": "title updated menu 1",
        "description": "description updated menu 1",
    }


@pytest.fixture
async def update_submenu_data():
    return {
        "title": "title updated submenu 1",
        "description": "description updated submenu 1",
    }


@pytest.fixture
async def update_dish_data():
    return {
        "title": "title updated submenu 1",
        "description": "description updated submenu 1",
        "price": "99.99",
    }
