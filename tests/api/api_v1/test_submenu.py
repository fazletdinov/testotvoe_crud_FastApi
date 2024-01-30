from httpx import AsyncClient
import uuid

from fastapi import status


class TestSubmenu:
    def setup_class(self):
        self.submenu_id = None
        self.submenu_title = None
        self.submenu_description = None
        self.submenu_menu_id = None

    async def test_submenu_create(
        self,
        async_client: AsyncClient,
        menu_data: dict[str, str],
        submenu_data: dict[str, str],
    ) -> None:
        response_menu = await async_client.post("/menus", json=menu_data)

        assert response_menu.status_code == status.HTTP_201_CREATED
        self.__class__.submenu_menu_id = response_menu.json()["id"]

        response_submenu = await async_client.post(
            f"/menus/{self.submenu_menu_id}/submenus", json=submenu_data
        )

        assert response_submenu.status_code == status.HTTP_201_CREATED
        content = response_submenu.json()
        self.__class__.submenu_id = content["id"]
        self.__class__.submenu_title = content["title"]
        self.__class__.submenu_description = content["description"]

    async def test_get_submenu(
        self, async_client: AsyncClient, submenu_data: dict[str, str]
    ) -> None:
        response_submenu = await async_client.get(
            url=f"/menus/{self.submenu_menu_id}/submenus/{self.submenu_id}"
        )
        assert response_submenu.status_code == status.HTTP_200_OK
        content = response_submenu.json()
        assert self.submenu_id == content["id"]
        assert self.submenu_title == content["title"]
        assert self.submenu_description == content["description"]
        assert "dishes_count" in content

    async def test_get_submenu_not_found(
        self, async_client: AsyncClient
    ) -> None:
        submenu_id = uuid.uuid4()
        response = await async_client.get(
            url=f"/menus/{self.submenu_menu_id}/submenus/{submenu_id}"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content: dict[str, str] = response.json()
        assert content["detail"] == "submenu not found"

    async def test_update_submenu(
        self, async_client: AsyncClient, update_submenu_data: dict[str, str]
    ) -> None:
        response = await async_client.patch(
            url=f"/menus/{self.submenu_menu_id}/submenus/{self.submenu_id}",
            json=update_submenu_data,
        )
        assert response.status_code == status.HTTP_200_OK

        content = response.json()
        assert content["id"] == self.submenu_id
        assert content["title"] != self.submenu_title
        assert content["description"] != self.submenu_description
        assert "dishes_count" in content

        self.submenu_title = content["title"]
        self.submenu_description = content["description"]

    async def test_update_submenu_not_found(
        self, async_client: AsyncClient, update_submenu_data: dict[str, str]
    ) -> None:
        submenu_id = uuid.uuid4()
        response = await async_client.patch(
            url=f"/menus/{self.submenu_menu_id}/submenus/{submenu_id}",
            json=update_submenu_data,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content = response.json()
        assert content["detail"] == "submenu not found"

    async def test_delete_submenu(self, async_client: AsyncClient) -> None:
        response = await async_client.delete(
            url=f"/menus/{self.submenu_menu_id}/submenus/{self.submenu_id}"
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
        self, async_client: AsyncClient
    ) -> None:
        response = await async_client.delete(
            url=f"/menus/{self.submenu_menu_id}/submenus/{self.submenu_id}"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content = response.json()
        assert content["detail"] == "submenu not found"

        assert "id" not in content
        assert "title" not in content
        assert "description" not in content
        assert "dishes_count" not in content

    async def test_get_submenus_not_found(
        self, async_client: AsyncClient
    ) -> None:
        response = await async_client.get(
            url=f"/menus/{self.submenu_menu_id}/submenus"
        )
        assert response.status_code == status.HTTP_200_OK
        content = response.json()
        assert content == []
