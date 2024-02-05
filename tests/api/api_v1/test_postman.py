from fastapi import status
from httpx import AsyncClient

from tests.conftest import reverse_url


class TestPostman:
    def setup_class(self):
        self.dish_submenu_id = None
        self.dish_submenu_menu_id = None

    async def test_create_dish(
            self,
            menu_data,
            dish_data,
            submenu_data,
            async_client: AsyncClient,
    ) -> None:
        dish_data_2: dict[str, str] = {
            'title': 'title dish 2',
            'description': 'description dish 2',
            'price': '55.50',
        }
        response_menu = await async_client.post(
            url=reverse_url('post_menu'),
            json=menu_data,
        )
        assert response_menu.status_code == status.HTTP_201_CREATED
        self.__class__.dish_submenu_menu_id = response_menu.json()['id']

        response_submenu = await async_client.post(
            url=reverse_url('post_submenu',
                            menu_id=self.dish_submenu_menu_id),
            json=submenu_data,
        )
        assert response_submenu.status_code == status.HTTP_201_CREATED
        self.__class__.dish_submenu_id = response_submenu.json()['id']

        response_dish_1 = await async_client.post(
            url=reverse_url('post_dish',
                            menu_id=self.dish_submenu_menu_id,
                            submenu_id=self.dish_submenu_id),
            json=dish_data,
        )
        assert response_dish_1.status_code == status.HTTP_201_CREATED

        response_dish_2 = await async_client.post(
            url=reverse_url('post_dish',
                            menu_id=self.dish_submenu_menu_id,
                            submenu_id=self.dish_submenu_id),
            json=dish_data_2,
        )
        assert response_dish_2.status_code == status.HTTP_201_CREATED

    async def test_get_menu(self, async_client: AsyncClient) -> None:
        response = await async_client.get(
            url=reverse_url('get_menu',
                            menu_id=self.dish_submenu_menu_id)
        )
        assert response.status_code == status.HTTP_200_OK
        content_get_menu = response.json()

        assert content_get_menu['dishes_count'] == 2
        assert content_get_menu['submenus_count'] == 1

    async def test_get_submenu(self, async_client: AsyncClient) -> None:
        response_get_submenu = await async_client.get(
            url=reverse_url('get_submenu',
                            menu_id=self.dish_submenu_menu_id,
                            submenu_id=self.dish_submenu_id)
        )
        assert response_get_submenu.status_code == status.HTTP_200_OK

        content_get_submenu = response_get_submenu.json()
        assert content_get_submenu['dishes_count'] == 2

    async def test_delete_submenu(self, async_client: AsyncClient) -> None:
        response_delete_submenu = await async_client.delete(
            url=reverse_url('delete_submenu',
                            menu_id=self.dish_submenu_menu_id,
                            submenu_id=self.dish_submenu_id)
        )
        assert response_delete_submenu.status_code == status.HTTP_200_OK
        content_delete_submenu = response_delete_submenu.json()

        assert content_delete_submenu['status'] is True
        assert (
            content_delete_submenu['message'] == 'The submenu has been deleted'
        )

    async def test_get_submenus(self, async_client: AsyncClient) -> None:
        response_list_submenu = await async_client.get(
            url=reverse_url('get_submenus',
                            menu_id=self.dish_submenu_menu_id)
        )
        assert response_list_submenu.status_code == status.HTTP_200_OK
        content_list_submenu = response_list_submenu.json()

        assert content_list_submenu == []

    async def test_get_dishes(self, async_client: AsyncClient) -> None:
        response_list_dish = await async_client.get(
            url=reverse_url('get_dishes',
                            menu_id=self.dish_submenu_menu_id,
                            submenu_id=self.dish_submenu_id)
        )
        assert response_list_dish.status_code == status.HTTP_200_OK

        content_list_dish = response_list_dish.json()
        assert content_list_dish == []

    async def test_get_menu_1(
            self, async_client: AsyncClient, menu_data
    ) -> None:
        response_get_menu = await async_client.get(
            url=reverse_url('get_menu',
                            menu_id=self.dish_submenu_menu_id)
        )
        assert response_get_menu.status_code == status.HTTP_200_OK
        content_get_menu = response_get_menu.json()

        assert content_get_menu['dishes_count'] == 0
        assert content_get_menu['submenus_count'] == 0

    async def test_delete_menu(self, async_client: AsyncClient) -> None:
        response_delete_menu = await async_client.delete(
            url=reverse_url('delete_menu',
                            menu_id=self.dish_submenu_menu_id)
        )
        assert response_delete_menu.status_code == status.HTTP_200_OK
        content_delete_menu = response_delete_menu.json()
        assert content_delete_menu['status'] is True
        assert content_delete_menu['message'] == 'The menu has been deleted'

    async def test_get_menus(self, async_client: AsyncClient) -> None:
        response_list_menu = await async_client.get(url=reverse_url('get_menus'))
        assert response_list_menu.status_code == status.HTTP_200_OK
        content_list_menu = response_list_menu.json()
        assert content_list_menu == []
