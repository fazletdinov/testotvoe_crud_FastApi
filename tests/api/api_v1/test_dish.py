from httpx import AsyncClient
import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.dish import DishDAL
from src.schemas.dish import DishCreate
from src.database.models.menu import Menu
from src.database.models.submenu import Submenu


async def test_create_dish(
    async_client: AsyncClient,
    db: AsyncSession,
    create_menu: Menu,
    create_submenu: Submenu,
) -> None:
    data_dish: dict[str, str] = {
        "title": "title dish 1",
        "description": "description dish 1",
        "price": "12.50",
    }
    response = await async_client.post(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}/dishes",
        json=data_dish,
    )
    assert response.status_code == status.HTTP_201_CREATED
    content = response.json()
    assert content["title"] == data_dish["title"]
    assert content["description"] == data_dish["description"]
    assert content["price"] == data_dish["price"]

    assert "id" in content


async def test_get_dish(
    async_client: AsyncClient,
    db: AsyncSession,
    create_menu: Menu,
    create_submenu: Submenu,
) -> None:
    data_dish: dict[str, str] = {
        "title": "title dish 1",
        "description": "description dish 1",
        "price": "12.50",
    }
    dish_crud = DishDAL(db)
    dish_body: DishCreate = DishCreate(**data_dish)
    dish = await dish_crud.create(create_submenu.id, dish_body)
    response = await async_client.get(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}"
        f"/dishes/{dish.id}"
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data_dish["title"]
    assert content["description"] == data_dish["description"]
    assert content["price"] == data_dish["price"]

    assert "id" in content


async def test_get_dish_not_found(
    async_client: AsyncClient,
    db: AsyncSession,
    create_menu: Menu,
    create_submenu: Submenu,
) -> None:
    dish_id = uuid.uuid4()
    response = await async_client.get(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}"
        f"/dishes/{dish_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "dish not found"


async def test_update_dish(
    async_client: AsyncClient,
    db: AsyncSession,
    create_menu: Menu,
    create_submenu: Submenu,
) -> None:
    data_dish: dict[str, str] = {
        "title": "title dish 1",
        "description": "description dish 1",
        "price": "12.50",
    }
    data_dish_update: dict[str, str] = {
        "title": "title dish 2",
        "description": "description dish 2",
        "price": "99.99",
    }
    dish_crud = DishDAL(db)
    dish_body: DishCreate = DishCreate(**data_dish)
    dish = await dish_crud.create(create_submenu.id, dish_body)
    response = await async_client.patch(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}"
        f"/dishes/{dish.id}",
        json=data_dish_update,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data_dish_update["title"]
    assert content["description"] == data_dish_update["description"]
    assert content["price"] == data_dish_update["price"]
    assert "id" in content

    assert content["title"] != data_dish["title"]
    assert content["description"] != data_dish["description"]
    assert content["price"] != data_dish["price"]


async def test_update_dish_not_found(
    async_client: AsyncClient,
    db: AsyncSession,
    create_menu: Menu,
    create_submenu: Submenu,
) -> None:
    data_dish: dict[str, str] = {
        "title": "title dish 1",
        "description": "description dish 1",
        "price": "12.50",
    }
    dish_id = uuid.uuid4()
    response = await async_client.patch(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}"
        f"/dishes/{dish_id}",
        json=data_dish,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "dish not found"

    assert "id" not in content
    assert "title" not in content
    assert "description" not in content
    assert "price" not in content


async def test_delete_dish(
    async_client: AsyncClient,
    db: AsyncSession,
    create_menu: Menu,
    create_submenu: Submenu,
) -> None:
    data_dish: dict[str, str] = {
        "title": "title dish 1",
        "description": "description dish 1",
        "price": "12.50",
    }
    dish_crud = DishDAL(db)
    dish_body: DishCreate = DishCreate(**data_dish)
    dish = await dish_crud.create(create_submenu.id, dish_body)
    response = await async_client.delete(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}"
        f"/dishes/{dish.id}"
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()

    assert content["status"] is True
    assert content["message"] == "The dish has been deleted"

    assert "id" not in content
    assert "title" not in content
    assert "description" not in content
    assert "price" not in content


async def test_delete_dish_not_found(
    async_client: AsyncClient,
    db: AsyncSession,
    create_menu: Menu,
    create_submenu: Submenu,
) -> None:
    dish_id = uuid.uuid4()
    response = await async_client.delete(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}"
        f"/dishes/{dish_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "dish not found"

    assert "id" not in content
    assert "title" not in content
    assert "description" not in content
    assert "price" not in content


async def test_get_dishes(
    async_client: AsyncClient,
    db: AsyncSession,
    create_menu: Menu,
    create_submenu: Submenu,
) -> None:
    data_dish_1: dict[str, str] = {
        "title": "title dish 1",
        "description": "description dish 1",
        "price": "12.50",
    }
    data_dish_2: dict[str, str] = {
        "title": "title dish 2",
        "description": "description dish 2",
        "price": "99.99",
    }
    dish_crud = DishDAL(db)
    dish_body_1: DishCreate = DishCreate(**data_dish_1)
    dish_body_2: DishCreate = DishCreate(**data_dish_2)
    await dish_crud.create(create_submenu.id, dish_body_1)
    await dish_crud.create(create_submenu.id, dish_body_2)
    response = await async_client.get(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}/dishes"
    )
    assert response.status_code == status.HTTP_200_OK
    content_1, content_2 = response.json()
    assert content_1["title"] == data_dish_1["title"]
    assert content_1["description"] == data_dish_1["description"]
    assert content_1["price"] == data_dish_1["price"]
    assert "id" in content_1

    assert content_2["title"] == data_dish_2["title"]
    assert content_2["description"] == data_dish_2["description"]
    assert content_2["price"] == data_dish_2["price"]
    assert "id" in content_2


async def test_get_dishes_not_found(
    async_client: AsyncClient,
    db: AsyncSession,
    create_menu: Menu,
    create_submenu: Submenu,
) -> None:
    response = await async_client.get(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}/dishes"
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content == []
