from httpx import AsyncClient
import uuid

from fastapi import status


class TestDish:
    def setup_class(self):
        self.dish_id = None
        self.dish_title = None
        self.dish_description = None
        self.dish_price = None
        self.dish_submenu_id = None
        self.dish_submenu_menu_id = None

    async def test_create_dish(
        self,
        async_client: AsyncClient,
        menu_data: dict[str, str],
        submenu_data: dict[str, str],
        dish_data: dict[str, str],
    ) -> None:
        response_menu = await async_client.post(
            url="/menus",
            json=menu_data,
        )
        self.__class__.dish_submenu_menu_id = response_menu.json()["id"]

        response_submenu = await async_client.post(
            f"/menus/{self.dish_submenu_menu_id}/submenus", json=submenu_data
        )
        self.__class__.dish_submenu_id = response_submenu.json()["id"]

        response_dish = await async_client.post(
            f"/menus/{self.dish_submenu_menu_id}/submenus/"
            f"{self.dish_submenu_id}/dishes",
            json=dish_data,
        )

        assert response_dish.status_code == status.HTTP_201_CREATED
        self.__class__.dish_id = response_dish.json()["id"]
        self.__class__.dish_title = response_dish.json()["title"]
        self.__class__.dish_description = response_dish.json()["description"]
        self.__class__.dish_price = response_dish.json()["price"]

    async def test_get_dish(
        self,
        async_client: AsyncClient,
    ) -> None:
        response_dish = await async_client.get(
            url=f"/menus/{self.dish_submenu_menu_id}/submenus/"
            f"{self.dish_submenu_id}"
            f"/dishes/{self.dish_id}"
        )
        assert response_dish.status_code == status.HTTP_200_OK
        content = response_dish.json()
        assert content["id"] == self.dish_id
        assert content["title"] == self.dish_title
        assert content["description"] == self.dish_description
        assert content["price"] == self.dish_price

    async def test_get_dish_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        dish_id = uuid.uuid4()
        response = await async_client.get(
            url=f"/menus/{self.dish_submenu_menu_id}/submenus/"
            f"{self.dish_submenu_id}"
            f"/dishes/{dish_id}"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content = response.json()
        assert content["detail"] == "dish not found"

    async def test_update_dish(
        self, async_client: AsyncClient, update_dish_data: dict[str, str]
    ) -> None:
        response = await async_client.patch(
            url=f"/menus/{self.dish_submenu_menu_id}/submenus/"
            f"{self.dish_submenu_id}"
            f"/dishes/{self.dish_id}",
            json=update_dish_data,
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        assert self.dish_title != content["title"]
        assert self.dish_description != content["description"]
        assert self.dish_price != content["price"]

        self.dish_title = content["title"]
        self.dish_description = content["description"]
        self.dish_price = content["price"]

    async def test_update_dish_not_found(
        self, async_client: AsyncClient, update_dish_data: dict[str, str]
    ) -> None:
        dish_id = uuid.uuid4()
        response = await async_client.patch(
            url=f"/menus/{self.dish_submenu_menu_id}/submenus/"
            f"{self.dish_submenu_id}"
            f"/dishes/{dish_id}",
            json=update_dish_data,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content = response.json()
        assert content["detail"] == "dish not found"

        assert "id" not in content
        assert "title" not in content
        assert "description" not in content
        assert "price" not in content

    async def test_delete_dish(
        self,
        async_client: AsyncClient,
    ) -> None:
        response = await async_client.delete(
            url=f"/menus/{self.dish_submenu_menu_id}/submenus/"
            f"{self.dish_submenu_id}"
            f"/dishes/{self.dish_id}"
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
        self,
        async_client: AsyncClient,
    ) -> None:
        response = await async_client.delete(
            url=f"/menus/{self.dish_submenu_menu_id}/submenus/"
            f"{self.dish_submenu_id}"
            f"/dishes/{self.dish_id}"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content = response.json()
        assert content["detail"] == "dish not found"

        assert "id" not in content
        assert "title" not in content
        assert "description" not in content
        assert "price" not in content

    async def test_get_dishes_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        response = await async_client.get(
            url=f"/menus/{self.dish_submenu_menu_id}/submenus/"
            f"{self.dish_submenu_id}/dishes"
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content == []
