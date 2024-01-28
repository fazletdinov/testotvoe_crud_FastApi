from typing import Any

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.schemas.dish import DishCreate
from src.crud.dish import DishDAL
from src.database.models.submenu import Submenu


@pytest.mark.parametrize(
    "title, description, price, expectation",
    [
        (
            123.45,
            "description dish 1",
            "12.60",
            pytest.raises(ValidationError),
        ),
        (
            "title dish 2",
            ["description dish 2"],
            "213",
            pytest.raises(ValidationError),
        ),
        (12345, 21414, 123, pytest.raises(ValidationError)),
        ("title dish 3", 21414, "Hello", pytest.raises(ValidationError)),
        (12345, "description dish 3", "43", pytest.raises(ValidationError)),
    ],
)
async def test_create_dish_raise(
    title,
    description,
    price,
    expectation,
    create_submenu: Submenu,
    db: AsyncSession,
) -> None:
    data_dish: dict[str, Any] = {
        "title": title,
        "description": description,
        "price": price,
    }
    dish_crud = DishDAL(db)
    with expectation:
        dish_body = DishCreate(**data_dish)
        await dish_crud.create(create_submenu.id, dish_body)


@pytest.mark.parametrize(
    "title, description, price",
    [
        ("title dish 1", "description dish 1", "12.50"),
        ("title dish 2", "description dish 2", "99.50"),
        ("title dish 3", "description dish 3", "102.50"),
    ],
)
async def test_create_dish_passed(
    title, description, price, create_submenu: Submenu, db: AsyncSession
) -> None:
    data_dish: dict[str, str] = {
        "title": title,
        "description": description,
        "price": price,
    }
    dish_crud = DishDAL(db)
    dish_body = DishCreate(**data_dish)
    dish_created = await dish_crud.create(create_submenu.id, dish_body)
    assert dish_created.title == data_dish["title"]
    assert dish_created.description == data_dish["description"]


@pytest.mark.parametrize(
    "title, description, price",
    [
        ("title dish 1", "description dish 1", "12.60"),
        ("title dish 2", "description dish 2", "13.60"),
        ("title dish 3", "description dish 3", "14.60"),
        ("title dish 4", "description dish 4", "15.60"),
    ],
)
async def test_get_dish(
    title, description, price, create_submenu: Submenu, db: AsyncSession
) -> None:
    data_dish: dict[str, str] = {
        "title": title,
        "description": description,
        "price": price,
    }
    dish_crud = DishDAL(db)
    dish_body = DishCreate(**data_dish)
    dish_created = await dish_crud.create(create_submenu.id, dish_body)
    get_dish = await dish_crud.get(create_submenu.id, dish_created.id)
    assert dish_created.id == get_dish.id
    assert dish_created.title == get_dish.title
    assert dish_created.description == get_dish.description
    assert dish_created.price == get_dish.price


@pytest.mark.parametrize(
    "dish_id, expectation",
    [
        ("hello", pytest.raises(HTTPException)),
        ("23", pytest.raises(HTTPException)),
    ],
)
async def test_get_dish_raise(
    dish_id, expectation, create_submenu: Submenu, db: AsyncSession
) -> None:
    dish_crud = DishDAL(db)
    with expectation:
        await dish_crud.get(create_submenu.id, dish_id)


@pytest.mark.parametrize(
    "title, description, price",
    [
        ("title dish 1", "description dish 1", "15.89"),
        ("title dish 2", "description dish 2", "7.89"),
        ("title dish 3", "description dish 3", "19.89"),
    ],
)
async def test_update_dish_passed(
    title, description, price, create_submenu: Submenu, db: AsyncSession
) -> None:
    data_dish: dict[str, str] = {
        "title": "title test",
        "description": "description test",
        "price": "00.00",
    }
    dish_crud = DishDAL(db)
    dish_body = DishCreate(**data_dish)
    dish_created = await dish_crud.create(create_submenu.id, dish_body)
    data_menu_for_update: dict[str, str] = {
        "title": title,
        "description": description,
        "price": price,
    }
    dish_updated = await dish_crud.update(
        create_submenu.id, dish_created.id, data_menu_for_update
    )
    assert dish_updated.id == dish_created.id
    assert dish_updated.title == data_menu_for_update["title"]
    assert dish_updated.description == data_menu_for_update["description"]
    assert dish_updated.price == data_menu_for_update["price"]


@pytest.mark.parametrize(
    "title, description, price, expectation",
    [
        (122234, "description price 1", "34.78", pytest.raises(HTTPException)),
        ("title price 2", 0.34525, "56.78", pytest.raises(HTTPException)),
        (
            ["title price 3"],
            "description price 3",
            12452,
            pytest.raises(HTTPException),
        ),
        (
            "title price 4",
            ("description price 4",),
            "23424",
            pytest.raises(HTTPException),
        ),
    ],
)
async def test_update_dish_raise(
    title,
    description,
    price,
    expectation,
    create_submenu: Submenu,
    db: AsyncSession,
) -> None:
    data_dish: dict[str, str] = {
        "title": "title menu 1",
        "description": "description menu 1",
        "price": "12.50",
    }
    dish_crud = DishDAL(db)
    dish_body = DishCreate(**data_dish)
    dish_created = await dish_crud.create(create_submenu.id, dish_body)
    data_menu_for_update: dict[str, Any] = {
        "title": title,
        "description": description,
        "price": price,
    }
    with expectation:
        await dish_crud.update(
            create_submenu.id, dish_created.id, data_menu_for_update
        )


@pytest.mark.parametrize(
    "title, description, price",
    [
        ("title dish 1", "description dish 1", "12.40"),
        ("title dish 2", "description dish 2", "05.40"),
        ("title dish 3", "description dish 3", "14.70"),
    ],
)
async def test_delete_dish_passed(
    title, description, price, create_submenu: Submenu, db: AsyncSession
) -> None:
    data_dish: dict[str, str] = {
        "title": title,
        "description": description,
        "price": price,
    }
    dish_crud = DishDAL(db)
    dish_body = DishCreate(**data_dish)
    dish_created = await dish_crud.create(create_submenu.id, dish_body)
    dish_id_deleted = await dish_crud.delete(
        create_submenu.id, dish_created.id
    )
    assert dish_id_deleted == dish_created.id


@pytest.mark.parametrize(
    "dish_id, expectation",
    [
        ("hello", pytest.raises(HTTPException)),
        (("tuple",), pytest.raises(HTTPException)),
    ],
)
async def test_delete_dish_raise(
    dish_id, expectation, create_submenu: Submenu, db: AsyncSession
) -> None:
    dish_crud = DishDAL(db)
    with expectation:
        await dish_crud.delete(create_submenu.id, dish_id)
