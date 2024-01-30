from httpx import AsyncClient
import uuid

from fastapi import status


class TestMenu:
    def setup_class(self):
        self.id = None
        self.title = None
        self.description = None

    async def test_create_menu(
        self, async_client: AsyncClient, menu_data: dict[str, str]
    ) -> None:
        response = await async_client.post(url="/menus", json=menu_data)
        assert response.status_code == status.HTTP_201_CREATED

        content: dict[str, str] = response.json()
        self.__class__.id = content["id"]
        self.__class__.title = content["title"]
        self.__class__.description = content["description"]

        assert content["title"] == menu_data["title"]
        assert content["description"] == menu_data["description"]
        assert "submenus_count" in content
        assert "dishes_count" in content

    async def test_get_menu(self, async_client: AsyncClient) -> None:
        response = await async_client.get(url=f"/menus/{self.id}")
        assert response.status_code == status.HTTP_200_OK

        content: dict[str, str] = response.json()
        assert content["title"] == self.title
        assert content["description"] == self.description

        assert "submenus_count" in content
        assert "dishes_count" in content
        assert "id" in content

    async def test_get_menu_not_found(self, async_client: AsyncClient) -> None:
        menu_id = uuid.uuid4()
        response = await async_client.get(url=f"/menus/{menu_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        content = response.json()
        assert content["detail"] == "menu not found"

    async def test_update_menu(
        self, async_client: AsyncClient, update_menu_data: dict[str, str]
    ) -> None:
        response = await async_client.patch(
            url=f"/menus/{self.id}", json=update_menu_data
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        assert content["title"] == update_menu_data["title"]
        assert content["description"] == update_menu_data["description"]

        assert content["title"] != self.title
        assert content["description"] != self.description

        self.title = content["title"]
        self.description = content["description"]

    async def test_update_menu_not_found(
        self, async_client: AsyncClient, update_menu_data
    ) -> None:
        menu_id = uuid.uuid4()
        response = await async_client.patch(
            url=f"/menus/{menu_id}", json=update_menu_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content = response.json()
        assert content["detail"] == "menu not found"

    async def test_delete_menu(self, async_client: AsyncClient) -> None:
        response = await async_client.delete(url=f"/menus/{self.id}")
        assert response.status_code == status.HTTP_200_OK

        content = response.json()
        assert content["status"] is True
        assert content["message"] == "The menu has been deleted"

        assert "id" not in content
        assert "title" not in content
        assert "description" not in content
        assert "dishes_count" not in content
        assert "submenus_count" not in content

    async def test_delete_menu_not_found(
        self, async_client: AsyncClient
    ) -> None:
        response = await async_client.delete(url=f"/menus/{self.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content = response.json()
        assert content["detail"] == "menu not found"

    async def test_get_menus_not_found(
        self, async_client: AsyncClient
    ) -> None:
        response = await async_client.get(url="/menus")
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content == []
