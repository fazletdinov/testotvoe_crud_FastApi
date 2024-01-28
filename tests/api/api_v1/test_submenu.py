from httpx import AsyncClient
import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.menu import Menu
from src.crud.submenu import SubmenuDAL
from src.schemas.submenu import SubmenuCreate


async def test_submenu_create(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    data_submenu: dict[str, str] = {
        "title": "submenu title 1",
        "description": "submenu description 1",
    }
    response = await async_client.post(
        url=f"/menus/{create_menu.id}/submenus", json=data_submenu
    )
    assert response.status_code == status.HTTP_201_CREATED
    content = response.json()
    assert content["title"] == data_submenu["title"]
    assert content["description"] == data_submenu["description"]
    assert "id" in content
    assert "dishes_count" in content


async def test_get_submenu(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    data_submenu: dict[str, str] = {
        "title": "submenu title 1",
        "description": "submenu description 1",
    }
    submenu_crud = SubmenuDAL(db)
    submenu_body = SubmenuCreate(**data_submenu)
    submenu = await submenu_crud.create(create_menu.id, submenu_body)
    response = await async_client.get(
        url=f"/menus/{create_menu.id}/submenus/{submenu.id}"
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data_submenu["title"]
    assert content["description"] == data_submenu["description"]
    assert "id" in content
    assert "dishes_count" in content


async def test_get_submenu_not_found(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    submenu_id = uuid.uuid4()
    response = await async_client.get(
        url=f"/menus/{create_menu.id}/submenus/{submenu_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content: dict[str, str] = response.json()
    assert content["detail"] == "submenu not found"


async def test_get_submenus(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    data_submenu_1: dict[str, str] = {
        "title": "submenu title 1",
        "description": "submenu description 1",
    }
    data_submenu_2: dict[str, str] = {
        "title": "submenu title 2",
        "description": "submenu description 2",
    }
    submenu_crud = SubmenuDAL(db)
    submenu_body_1 = SubmenuCreate(**data_submenu_1)
    submenu_body_2 = SubmenuCreate(**data_submenu_2)
    await submenu_crud.create(create_menu.id, submenu_body_1)
    await submenu_crud.create(create_menu.id, submenu_body_2)
    response = await async_client.get(url=f"/menus/{create_menu.id}/submenus")
    assert response.status_code == status.HTTP_200_OK
    content_1, content_2 = response.json()

    assert content_1["title"] == data_submenu_1["title"]
    assert content_1["description"] == data_submenu_1["description"]
    assert "id" in content_1
    assert "dishes_count" in content_1

    assert content_2["title"] == data_submenu_2["title"]
    assert content_2["description"] == data_submenu_2["description"]
    assert "id" in content_2
    assert "dishes_count" in content_2


async def test_get_submenus_not_found(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    response = await async_client.get(url=f"/menus/{create_menu.id}/submenus")
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content == []


async def test_update_submenu(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    data_submenu: dict[str, str] = {
        "title": "submenu title 1",
        "description": "submenu description 1",
    }
    data_submenu_update: dict[str, str] = {
        "title": "submenu title 2",
        "description": "submenu description 2",
    }
    submenu_crud = SubmenuDAL(db)
    submenu_body: SubmenuCreate = SubmenuCreate(**data_submenu)
    submenu = await submenu_crud.create(create_menu.id, submenu_body)
    response = await async_client.patch(
        url=f"/menus/{create_menu.id}/submenus/{submenu.id}",
        json=data_submenu_update,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == data_submenu_update["title"]
    assert content["description"] == data_submenu_update["description"]
    assert "id" in content
    assert "dishes_count" in content

    assert content["title"] != data_submenu["title"]
    assert content["description"] != data_submenu["description"]


async def test_update_submenu_not_found(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    data_submenu: dict[str, str] = {
        "title": "submenu title 1",
        "description": "submenu description 1",
    }
    submenu_id = uuid.uuid4()
    response = await async_client.patch(
        url=f"/menus/{create_menu.id}/submenus/{submenu_id}", json=data_submenu
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "submenu not found"


async def test_delete_submenu(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    data_submenu: dict[str, str] = {
        "title": "submenu title 1",
        "description": "submenu description 1",
    }
    submenu_crud = SubmenuDAL(db)
    submenu_body: SubmenuCreate = SubmenuCreate(**data_submenu)
    submenu = await submenu_crud.create(create_menu.id, submenu_body)
    response = await async_client.delete(
        url=f"/menus/{create_menu.id}/submenus/{submenu.id}"
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()

    assert content["status"] is True
    assert content["message"] == "The submenu has been deleted"

    assert "id" not in content
    assert "title" not in content
    assert "description" not in content
    assert "dishes_count" not in content


async def test_delete_submenu_not_found(
    async_client: AsyncClient, db: AsyncSession, create_menu: Menu
) -> None:
    submenu_id = uuid.uuid4()
    response = await async_client.delete(
        url=f"/menus/{create_menu.id}/submenus/{submenu_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content = response.json()
    assert content["detail"] == "submenu not found"

    assert "id" not in content
    assert "title" not in content
    assert "description" not in content
    assert "dishes_count" not in content
