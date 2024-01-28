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
from src.crud.menu import MenuDAL
from src.crud.submenu import SubmenuDAL
from src.schemas.submenu import SubmenuCreate
from src.database.models.menu import Menu

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


@pytest.fixture(autouse=True)
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
        app=app, base_url="http://localhost:8000/api/v1", follow_redirects=True
    ) as aclient:
        yield aclient


@pytest.fixture(scope="session")
async def db() -> AsyncGenerator[AsyncSession, None]:
    session = get_scoped_session()
    yield session
    await session.close()


@pytest.fixture
async def create_menu(db: AsyncSession):
    data_menu = {"title": "title menu 1", "description": "description menu 1"}
    menu_crud = MenuDAL(db)
    return await menu_crud.create(data_menu)


@pytest.fixture
async def create_submenu(create_menu: Menu, db: AsyncSession):
    data_submenu = {
        "title": "title submenu 1",
        "description": "description submenu 1",
    }
    submenu_crud = SubmenuDAL(db)
    submenu_body = SubmenuCreate(**data_submenu)
    return await submenu_crud.create(create_menu.id, submenu_body)
