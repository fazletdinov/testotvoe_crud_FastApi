import asyncio
from asyncio import current_task
from typing import AsyncGenerator
from uuid import UUID

import backoff
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from main import app
from src.core.config import settings
from src.database.models import Base
from src.database.redis_cache import RedisDB, get_redis
from src.database.session import db_helper

async_engine = create_async_engine(
    url=settings.db_test.async_url, echo=False, poolclass=StaticPool
)
async_session_factory = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

Base.metadata.bind = async_engine


async def override_scoped_session_dependency():
    scoped_factory = async_scoped_session(
        async_session_factory,
        scopefunc=current_task,
    )
    try:
        async with scoped_factory() as session:
            yield session
    finally:
        await scoped_factory.remove()


@backoff.on_exception(backoff.expo, ConnectionError, max_tries=5, raise_on_giveup=True)
async def override_get_redis() -> RedisDB:
    return RedisDB(host=settings.redis_test.host,
                   port=settings.redis_test.port,
                   password=settings.redis_test.password.get_secret_value(),
                   expire_in_sec=settings.redis_test.expire_in_sec)


app.dependency_overrides[
    db_helper.scoped_session_dependency
] = override_scoped_session_dependency
app.dependency_overrides[get_redis] = override_get_redis


@pytest.fixture(autouse=True, scope='class')
async def async_db_engine() -> AsyncGenerator:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
            app=app,
            base_url=f'{settings.db_test.API_V1_STR}',
            follow_redirects=True,
    ) as aclient:
        yield aclient


@pytest.fixture(scope='session')
async def db() -> AsyncGenerator[AsyncSession, None]:
    scoped_factory = async_scoped_session(
        async_session_factory,
        scopefunc=current_task,
    )
    try:
        async with scoped_factory() as session:
            yield session
    finally:
        await scoped_factory.remove()


@pytest.fixture
async def menu_data():
    return {
        'title': 'title menu 1',
        'description': 'description menu description 1',
    }


@pytest.fixture
async def submenu_data():
    return {
        'title': 'title submenu 1',
        'description': 'description submenu description 1',
    }


@pytest.fixture
async def dish_data():
    return {
        'title': 'title dish 1',
        'description': 'description dish description 1',
        'price': '77.77',
    }


@pytest.fixture
async def update_menu_data():
    return {
        'title': 'title updated menu 1',
        'description': 'description updated menu 1',
    }


@pytest.fixture
async def update_submenu_data():
    return {
        'title': 'title updated submenu 1',
        'description': 'description updated submenu 1',
    }


@pytest.fixture
async def update_dish_data():
    return {
        'title': 'title updated submenu 1',
        'description': 'description updated submenu 1',
        'price': '99.99',
    }


def reverse_url(route_name: str, **kwargs: UUID) -> str:
    routes = {
        'get_menus': '/menus',
        'create_menu': '/menus',
        'get_menu': f'/menus/{kwargs.get("menu_id", "")}',
        'update_menu': f'/menus/{kwargs.get("menu_id", "")}',
        'delete_menu': f'/menus/{kwargs.get("menu_id", "")}',
        'get_submenus': f'/menus/{kwargs.get("menu_id", "")}/submenus',
        'create_submenu': f'/menus/{kwargs.get("menu_id", "")}/submenus',
        'get_submenu': f'/menus/{kwargs.get("menu_id", "")}/submenus/{kwargs.get("submenu_id", "")}',
        'update_submenu': f'/menus/{kwargs.get("menu_id", "")}/submenus/{kwargs.get("submenu_id", "")}',
        'delete_submenu': f'/menus/{kwargs.get("menu_id", "")}/submenus/{kwargs.get("submenu_id", "")}',
        'get_dishes': f'/menus/{kwargs.get("menu_id", "")}/submenus/{kwargs.get("submenu_id", "")}/dishes',
        'create_dish': f'/menus/{kwargs.get("menu_id", "")}/submenus/{kwargs.get("submenu_id", "")}/dishes',
        'get_dish': f'/menus/{kwargs.get("menu_id", "")}/submenus/'
                    f'{kwargs.get("submenu_id", "")}/dishes/{kwargs.get("dish_id", "")}',
        'update_dish': f'/menus/{kwargs.get("menu_id", "")}/submenus/'
                       f'{kwargs.get("submenu_id", "")}/dishes/{kwargs.get("dish_id", "")}',
        'delete_dish': f'/menus/{kwargs.get("menu_id", "")}/submenus/'
                       f'{kwargs.get("submenu_id", "")}/dishes/{kwargs.get("dish_id", "")}',
    }

    return str(routes.get(route_name))
