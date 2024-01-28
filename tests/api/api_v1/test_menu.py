from httpx import AsyncClient
import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.menu import MenuDAL
from src.database.models.menu import Menu


async def test_create_menu(async_client: AsyncClient) -> None:
    data: dict[str, str] = {
        "title": "menu title 1",
        "description": "menu description 1",
    }
    response = await async_client.post(url="/menus", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "submenus_count" in content
    assert "dishes_count" in content


async def test_get_menu(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    response = await async_client.get(url=f"/menus/{create_menu.id}")
    assert response.status_code == status.HTTP_200_OK
    content: dict[str, str] = response.json()
    assert content["title"] == create_menu.title
    assert content["description"] == create_menu.description
    assert "submenus_count" in content
    assert "dishes_count" in content
    assert "id" in content


async def test_get_menu_not_found(async_client: AsyncClient) -> None:
    menu_id = uuid.uuid4()
    response = await async_client.get(url=f"/menus/{menu_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "menu not found"


async def test_update_menu(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    data_update: dict[str, str] = {
        "title": "menu title 3",
        "description": "menu description 3",
    }
    response = await async_client.patch(
        url=f"/menus/{create_menu.id}", json=data_update
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data_update["title"]
    assert content["description"] == data_update["description"]
    assert content["title"] != create_menu.title
    assert content["description"] != create_menu.description
    assert "id" in content
    assert "dishes_count" in content
    assert "submenus_count" in content


async def test_update_menu_not_found(async_client: AsyncClient) -> None:
    data: dict[str, str] = {
        "title": "menu title 1",
        "description": "menu description 1",
    }
    menu_id = uuid.uuid4()
    response = await async_client.patch(url=f"/menus/{menu_id}", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "menu not found"


async def test_get_menus(async_client: AsyncClient, db: AsyncSession) -> None:
    data_1: dict[str, str] = {
        "title": "menu title 1",
        "description": "menu description 1",
    }
    data_2: dict[str, str] = {
        "title": "menu title 2",
        "description": "menu description 2",
    }
    menu_crud = MenuDAL(db)
    menu_1 = await menu_crud.create(data_1)
    menu_2 = await menu_crud.create(data_2)
    response = await async_client.get(url="/menus/")
    assert response.status_code == status.HTTP_200_OK
    content_1, content_2 = response.json()
    assert content_1["title"] == menu_1.title
    assert content_1["description"] == menu_1.description
    assert "dishes_count" in content_1
    assert "submenus_count" in content_1
    assert "id" in content_1

    assert content_2["title"] == menu_2.title
    assert content_2["description"] == menu_2.description
    assert "dishes_count" in content_2
    assert "submenus_count" in content_2
    assert "id" in content_2


async def test_get_menus_not_found(async_client: AsyncClient) -> None:
    response = await async_client.get(url="/menus")
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content == []


async def test_delete_menu(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    response = await async_client.delete(url=f"/menus/{create_menu.id}")
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["status"] is True
    assert content["message"] == "The menu has been deleted"

    assert "id" not in content
    assert "title" not in content
    assert "description" not in content
    assert "dishes_count" not in content
    assert "submenus_count" not in content


async def test_delete_menu_not_found(async_client: AsyncClient) -> None:
    menu_id = uuid.uuid4()
    response = await async_client.delete(url=f"/menus/{menu_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "menu not found"
