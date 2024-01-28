from typing import Any

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.menu import MenuDAL


@pytest.mark.parametrize(
    "title, description, expectation",
    [
        (123.45, "description menu 1", pytest.raises(HTTPException)),
        ("title menu 2", ["description menu 2"], pytest.raises(HTTPException)),
        (12345, 21414, pytest.raises(HTTPException)),
        ("title menu 3", 21414, pytest.raises(HTTPException)),
        (12345, "description menu 3", pytest.raises(HTTPException)),
    ],
)
async def test_create_menu_raise(
    title, description, expectation, db: AsyncSession
) -> None:
    data_menu: dict[str, Any] = {"title": title, "description": description}
    menu_crud = MenuDAL(db)
    with expectation:
        await menu_crud.create(data_menu)


@pytest.mark.parametrize(
    "title, description",
    [
        ("title menu 1", "description menu 1"),
        ("title menu 2", "description menu 2"),
        ("title menu 3", "description menu 3"),
    ],
)
async def test_create_menu_passed(
    title, description, db: AsyncSession
) -> None:
    data_menu: dict[str, str] = {"title": title, "description": description}
    menu_crud = MenuDAL(db)
    menu_created = await menu_crud.create(data_menu)
    assert menu_created.title == data_menu["title"]
    assert menu_created.description == data_menu["description"]


@pytest.mark.parametrize(
    "title, description",
    [
        ("title menu 1", "description menu 1"),
        ("title menu 2", "description menu 2"),
        ("title menu 3", "description menu 3"),
        ("title menu 4", "description menu 4"),
    ],
)
async def test_get_menu(title, description, db: AsyncSession) -> None:
    data_menu: dict[str, str] = {"title": title, "description": description}
    menu_crud = MenuDAL(db)
    menu_created = await menu_crud.create(data_menu)
    get_menu = await menu_crud.get(menu_created.id)
    assert menu_created.id == get_menu.id
    assert menu_created.title == get_menu.title
    assert menu_created.description == get_menu.description
    assert menu_created.submenus_count == get_menu.submenus_count
    assert menu_created.dishes_count == get_menu.dishes_count


@pytest.mark.parametrize(
    "menu_id, expectation",
    [
        (1, pytest.raises(HTTPException)),
        (2.45, pytest.raises(HTTPException)),
        ("hello", pytest.raises(HTTPException)),
        ("23", pytest.raises(HTTPException)),
    ],
)
async def test_get_menu_raise(menu_id, expectation, db: AsyncSession) -> None:
    menu_crud = MenuDAL(db)
    with expectation:
        await menu_crud.get(menu_id)


@pytest.mark.parametrize(
    "title, description",
    [
        ("title menu 1", "description menu 1"),
        ("title menu 2", "description menu 2"),
        ("title menu 3", "description menu 3"),
    ],
)
async def test_update_menu_passed(
    title, description, db: AsyncSession
) -> None:
    data_menu: dict[str, str] = {"title": title, "description": description}
    menu_crud = MenuDAL(db)
    menu_created = await menu_crud.create(data_menu)
    data_menu_for_update: dict = {
        "title": "title test",
        "description": "description test",
    }
    menu_updated = await menu_crud.update(
        menu_created.id, data_menu_for_update
    )
    assert menu_updated.id == menu_created.id
    assert menu_updated.submenus_count == menu_created.submenus_count
    assert menu_updated.dishes_count == menu_created.dishes_count
    assert menu_updated.title == data_menu_for_update["title"]
    assert menu_updated.description == data_menu_for_update["description"]


@pytest.mark.parametrize(
    "title, description, expectation",
    [
        (122234, "description menu 1", pytest.raises(HTTPException)),
        ("title menu 2", 0.34525, pytest.raises(HTTPException)),
        (["title menu 3"], "description menu 3", pytest.raises(HTTPException)),
        (
            "title menu 4",
            ("description menu 4",),
            pytest.raises(HTTPException),
        ),
    ],
)
async def test_update_menu_raise(
    title, description, expectation, db: AsyncSession
) -> None:
    data_menu: dict[str, str] = {
        "title": "title menu 1",
        "description": "description menu 1",
    }
    menu_crud = MenuDAL(db)
    menu_created = await menu_crud.create(data_menu)
    data_menu_for_update: dict[str, Any] = {
        "title": title,
        "description": description,
    }
    with expectation:
        await menu_crud.update(menu_created.id, data_menu_for_update)


@pytest.mark.parametrize(
    "title, description",
    [
        ("title menu 1", "description menu 1"),
        ("title menu 2", "description menu 2"),
        ("title menu 3", "description menu 3"),
    ],
)
async def test_delete_menu_passed(
    title, description, db: AsyncSession
) -> None:
    data_menu: dict[str, str] = {"title": title, "description": description}
    menu_crud = MenuDAL(db)
    menu_created = await menu_crud.create(data_menu)
    menu_id_deleted = await menu_crud.delete(menu_created.id)
    assert menu_id_deleted == menu_created.id


@pytest.mark.parametrize(
    "menu_id, expectation",
    [
        ("hello", pytest.raises(HTTPException)),
        (("tuple",), pytest.raises(HTTPException)),
    ],
)
async def test_delete_menu_raise(
    menu_id, expectation, db: AsyncSession
) -> None:
    menu_crud = MenuDAL(db)
    with expectation:
        await menu_crud.delete(menu_id)
