from fastapi import status
from httpx import AsyncClient

from src.database.models.menu import Menu
from src.database.models.submenu import Submenu


async def test_postman(
    create_menu: Menu, create_submenu: Submenu, async_client: AsyncClient
) -> None:
    data_dish_1: dict[str, str] = {
        "title": "title dish 1",
        "description": "description dish 1",
        "price": "12.50",
    }
    data_dish_2: dict[str, str] = {
        "title": "title dish 2",
        "description": "description dish 2",
        "price": "99.50",
    }
    await async_client.post(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}/dishes",
        json=data_dish_1,
    )
    await async_client.post(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}/dishes",
        json=data_dish_2,
    )

    response_menu = await async_client.get(url=f"/menus/{create_menu.id}")
    assert response_menu.status_code == status.HTTP_200_OK
    content_menu = response_menu.json()
    assert content_menu["title"] == create_menu.title
    assert content_menu["description"] == create_menu.description
    assert content_menu["dishes_count"] == 2
    assert content_menu["submenus_count"] == 1

    response_get_submenu = await async_client.get(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}"
    )
    assert response_get_submenu.status_code == status.HTTP_200_OK
    content_get_submenu = response_get_submenu.json()
    assert content_get_submenu["title"] == create_submenu.title
    assert content_get_submenu["description"] == create_submenu.description
    assert content_get_submenu["dishes_count"] == 2

    response_delete_submenu = await async_client.delete(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}"
    )
    assert response_delete_submenu.status_code == status.HTTP_200_OK
    content_delete_submenu = response_delete_submenu.json()
    assert content_delete_submenu["status"] is True
    assert content_delete_submenu["message"] == "The submenu has been deleted"

    response_list_submenu = await async_client.get(
        url=f"/menus/{create_menu.id}/submenus"
    )
    assert response_list_submenu.status_code == status.HTTP_200_OK
    content_list_submenu = response_list_submenu.json()
    assert content_list_submenu == []

    response_list_dish = await async_client.get(
        url=f"/menus/{create_menu.id}/submenus/{create_submenu.id}/dishes"
    )
    assert response_list_dish.status_code == status.HTTP_200_OK
    content_list_dish = response_list_dish.json()
    assert content_list_dish == []

    response_get_menu = await async_client.get(url=f"/menus/{create_menu.id}")
    assert response_get_menu.status_code == status.HTTP_200_OK
    content_get_menu = response_get_menu.json()
    assert content_get_menu["title"] == create_menu.title
    assert content_get_menu["description"] == create_menu.description
    assert content_get_menu["dishes_count"] == create_menu.dishes_count
    assert content_get_menu["submenus_count"] == create_menu.submenus_count

    response_delete_menu = await async_client.delete(
        url=f"/menus/{create_menu.id}"
    )
    assert response_delete_menu.status_code == status.HTTP_200_OK
    content_delete_menu = response_delete_menu.json()
    assert content_delete_menu["status"] is True
    assert content_delete_menu["message"] == "The menu has been deleted"

    response_list_menu = await async_client.get(url="/menus")
    assert response_list_menu.status_code == status.HTTP_200_OK
    content_list_menu = response_list_menu.json()
    assert content_list_menu == []
