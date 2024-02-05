from abc import ABCMeta, abstractmethod
from typing import Any
from uuid import UUID

from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.menu import MenuDAL
from src.database.models.menu import Menu
from src.database.redis_cache import RedisDB, get_redis
from src.database.session import db_helper
from src.schemas.menu import MenuCreate, MenuResponse


class MenuServiceBase(metaclass=ABCMeta):
    @abstractmethod
    async def create_menu(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get_menu(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get_menus_list(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def update_menu(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def delete_menu(self, *args: Any, **kwargs: Any) -> Any:
        pass


class MenuService(MenuServiceBase):
    def __init__(self, session: AsyncSession, cache: RedisDB) -> None:
        self.session = session
        self.cache = cache

    async def create_menu(self, body: MenuCreate, back_tasks: BackgroundTasks) -> MenuResponse:
        menu_crud = MenuDAL(self.session)
        menu = await menu_crud.create(body)
        back_tasks.add_task(self.cache.delete_cache, 'menu_list')
        return MenuResponse.model_validate(menu)

    async def get_menu(self, menu_id: UUID) -> MenuResponse | Exception:
        cache_menu = await self.cache.get_value(f'menu_{menu_id}')
        if cache_menu:
            data_menu = cache_menu
        else:
            menu_crud = MenuDAL(self.session)
            menu = await self.session.get(Menu, menu_id)
            if menu is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='menu not found'
                )
            menu = await menu_crud.get(menu_id)
            data_menu = MenuResponse.model_validate(menu)
            await self.cache.set_key(f'menu_{menu_id}', data_menu)
        return data_menu

    async def get_menus_list(
            self, offset: int, limit: int
    ) -> list[MenuResponse]:
        cache_menu_list = await self.cache.get_value('menu_list')
        if cache_menu_list:
            data_menu_list = cache_menu_list
        else:
            menu_crud = MenuDAL(self.session)
            menu_list = await menu_crud.get_list(offset, limit)
            data_menu_list = [MenuResponse.model_validate(menu) for menu in menu_list]
            await self.cache.set_all('menu_list', data_menu_list)
        return data_menu_list

    async def update_menu(
            self, menu_id: UUID, body: dict[str, str], back_tasks: BackgroundTasks
    ) -> MenuResponse | Exception:
        menu_crud = MenuDAL(self.session)
        menu = await self.session.get(Menu, menu_id)
        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='menu not found'
            )
        menu_updated = await menu_crud.update(menu_id, body)
        data_menu_update = MenuResponse.model_validate(menu_updated)
        await self.cache.set_key(f'menu_{menu_id}', data_menu_update)
        back_tasks.add_task(self.cache.delete_cache, 'menu_list')
        return data_menu_update

    async def delete_menu(self, menu_id: UUID, back_tasks: BackgroundTasks) -> Exception | None | UUID:
        menu_crud = MenuDAL(self.session)
        menu = await self.session.get(Menu, menu_id)
        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='menu not found'
            )
        menu_delete_id = await menu_crud.delete(menu_id)
        back_tasks.add_task(self.cache.delete_cache, f'menu_{menu_delete_id}')
        back_tasks.add_task(self.cache.delete_cache, 'menu_list')
        back_tasks.add_task(self.cache.delete_cache, 'submenu_list')
        back_tasks.add_task(self.cache.delete_cache, 'dish_list')
        return menu_delete_id


def get_menu_service(
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        redis_cache: RedisDB = Depends(get_redis),
) -> MenuService:
    return MenuService(session, cache=redis_cache)
