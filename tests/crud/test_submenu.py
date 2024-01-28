from typing import Any

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.crud.submenu import SubmenuDAL
from src.schemas.submenu import SubmenuCreate
from src.database.models.menu import Menu


@pytest.mark.parametrize(
    "title, description, expectation",
    [
        (123.45, "description submenu 1", pytest.raises(ValidationError)),
        (
            "title menu 2",
            ["description menu 2"],
            pytest.raises(ValidationError),
        ),
        (12345, 21414, pytest.raises(ValidationError)),
        ("title menu 3", 21414, pytest.raises(ValidationError)),
        (12345, "description submenu 3", pytest.raises(ValidationError)),
    ],
)
async def test_create_submenu_raise(
    title, description, expectation, create_menu: Menu, db: AsyncSession
) -> None:
    data_submenu: dict = {"title": title, "description": description}
    submenu_crud = SubmenuDAL(db)
    with expectation:
        submenu_body = SubmenuCreate(**data_submenu)
        await submenu_crud.create(create_menu.id, submenu_body)


@pytest.mark.parametrize(
    "title, description",
    [
        ("title submenu 1", "description submenu 1"),
        ("title submenu 2", "description submenu 2"),
        ("title submenu 3", "description submenu 3"),
    ],
)
async def test_create_submenu_passed(
    title, description, create_menu: Menu, db: AsyncSession
) -> None:
    data_submenu: dict[str, Any] = {"title": title, "description": description}
    submenu_crud = SubmenuDAL(db)
    submenu_body = SubmenuCreate(**data_submenu)
    submenu_created = await submenu_crud.create(create_menu.id, submenu_body)
    assert submenu_created.title == data_submenu["title"]
    assert submenu_created.description == data_submenu["description"]


@pytest.mark.parametrize(
    "title, description",
    [
        ("title submenu 1", "description submenu 1"),
        ("title submenu 2", "description submenu 2"),
        ("title submenu 3", "description submenu 3"),
        ("title submenu 4", "description submenu 4"),
    ],
)
async def test_get_submenu_passed(
    title, description, create_menu: Menu, db: AsyncSession
) -> None:
    data_submenu: dict[str, str] = {"title": title, "description": description}
    submenu_crud = SubmenuDAL(db)
    submenu_body = SubmenuCreate(**data_submenu)
    submenu_created = await submenu_crud.create(create_menu.id, submenu_body)
    get_submenu = await submenu_crud.get(create_menu.id, submenu_created.id)
    assert submenu_created.id == get_submenu.id
    assert submenu_created.title == get_submenu.title
    assert submenu_created.description == get_submenu.description
    assert submenu_created.dishes_count == get_submenu.dishes_count


@pytest.mark.parametrize(
    "submenu_id, expectation",
    [
        ("hello", pytest.raises(HTTPException)),
        ("23", pytest.raises(HTTPException)),
    ],
)
async def test_get_submenu_raise(
    submenu_id, expectation, create_menu: Menu, db: AsyncSession
) -> None:
    submenu_crud = SubmenuDAL(db)
    with expectation:
        await submenu_crud.get(create_menu.id, submenu_id)


@pytest.mark.parametrize(
    "title, description",
    [
        ("title submenu 1", "description submenu 1"),
        ("title submenu 2", "description submenu 2"),
        ("title submenu 3", "description submenu 3"),
    ],
)
async def test_update_submenu_passed(
    title, description, create_menu: Menu, db: AsyncSession
) -> None:
    data_submenu: dict[str, str] = {
        "title": "title test",
        "description": "description test",
    }
    submenu_crud = SubmenuDAL(db)
    submenu_body = SubmenuCreate(**data_submenu)
    submenu_created = await submenu_crud.create(create_menu.id, submenu_body)
    data_menu_for_update: dict[str, str] = {
        "title": title,
        "description": description,
    }
    submenu_updated = await submenu_crud.update(
        create_menu.id, submenu_created.id, data_menu_for_update
    )
    assert submenu_updated.id == submenu_created.id
    assert submenu_updated.dishes_count == submenu_created.dishes_count
    assert submenu_updated.title == data_menu_for_update["title"]
    assert submenu_updated.description == data_menu_for_update["description"]


@pytest.mark.parametrize(
    "title, description, expectation",
    [
        (122234, "description submenu 1", pytest.raises(HTTPException)),
        ("title submenu 2", 0.34525, pytest.raises(HTTPException)),
        (
            ["title submenu 3"],
            "description submenu 3",
            pytest.raises(HTTPException),
        ),
        (
            "title submenu 4",
            ("description submenu 4",),
            pytest.raises(HTTPException),
        ),
    ],
)
async def test_update_submenu_raise(
    title, description, expectation, create_menu: Menu, db: AsyncSession
) -> None:
    data_submenu: dict[str, str] = {
        "title": "title submenu 1",
        "description": "description submenu 1",
    }
    submenu_crud = SubmenuDAL(db)
    submenu_body = SubmenuCreate(**data_submenu)
    submenu_created = await submenu_crud.create(create_menu.id, submenu_body)
    data_menu_for_update: dict[str, Any] = {
        "title": title,
        "description": description,
    }
    with expectation:
        await submenu_crud.update(
            create_menu.id, submenu_created.id, data_menu_for_update
        )


@pytest.mark.parametrize(
    "title, description",
    [
        ("title submenu 1", "description submenu 1"),
        ("title submenu 2", "description submenu 2"),
        ("title submenu 3", "description submenu 3"),
    ],
)
async def test_delete_menu_passed(
    title, description, create_menu: Menu, db: AsyncSession
) -> None:
    data_submenu: dict[str, str] = {"title": title, "description": description}
    submenu_crud = SubmenuDAL(db)
    submenu_body = SubmenuCreate(**data_submenu)
    submenu_created = await submenu_crud.create(create_menu.id, submenu_body)
    submenu_id_deleted = await submenu_crud.delete(
        create_menu.id, submenu_created.id
    )
    assert submenu_id_deleted == submenu_created.id


@pytest.mark.parametrize(
    "submenu_id, expectation",
    [
        ("hello", pytest.raises(HTTPException)),
        (("tuple",), pytest.raises(HTTPException)),
    ],
)
async def test_delete_menu_raise(
    submenu_id, expectation, create_menu: Menu, db: AsyncSession
) -> None:
    submenu_crud = SubmenuDAL(db)
    with expectation:
        await submenu_crud.delete(create_menu.id, submenu_id)
