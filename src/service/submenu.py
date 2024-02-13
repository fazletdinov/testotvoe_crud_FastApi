from abc import ABCMeta, abstractmethod
from typing import Any
from uuid import UUID

from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.submenu import SubmenuDAL
from src.database.redis_cache import RedisDB, get_redis
from src.database.session import db_helper
from src.schemas.submenu import SubmenuCreate, SubmenuResponse


class SubmenuServiceBase(metaclass=ABCMeta):
    @abstractmethod
    async def create_submenu(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get_submenu(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get_submenus_list(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def update_submenu(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def delete_submenu(self, *args: Any, **kwargs: Any) -> Any:
        pass


class SubmenuService(SubmenuServiceBase):
    def __init__(self, session: AsyncSession, cache: RedisDB):
        self.session = session
        self.cache = cache

    async def create_submenu(
            self, menu_id: UUID, submenu_body: SubmenuCreate, back_tasks: BackgroundTasks
    ) -> SubmenuResponse:
        submenu_crud = SubmenuDAL(self.session)
        submenu = await submenu_crud.create(menu_id, submenu_body)
        back_tasks.add_task(self.cache.delete_cache, 'menu_list')
        back_tasks.add_task(self.cache.delete_cache, 'submenu_list')
        back_tasks.add_task(self.cache.delete_cache, 'full_menus_submenus_dishes')
        back_tasks.add_task(self.cache.delete_cache, f'menu_{menu_id}')
        return SubmenuResponse.model_validate(submenu)

    async def get_submenu(
            self, menu_id: UUID, submenu_id: UUID
    ) -> SubmenuResponse | Exception:
        cache_submenu = await self.cache.get_value(f'submenu_{submenu_id}')
        if cache_submenu:
            data_submenu = cache_submenu
        else:
            submenu_crud = SubmenuDAL(self.session)
            submenu = await submenu_crud.get(menu_id, submenu_id)
            if submenu is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='submenu not found',
                )
            data_submenu = SubmenuResponse.model_validate(submenu)
            await self.cache.set_key(f'submenu_{submenu_id}', data_submenu)
        return data_submenu

    async def get_submenus_list(
            self, menu_id: UUID, offset: int, limit: int
    ) -> list[SubmenuResponse]:
        cache_submenu_list = await self.cache.get_value('submenu_list')
        if cache_submenu_list:
            data_submenu_list = cache_submenu_list
        else:
            submenu_crud = SubmenuDAL(self.session)
            submenu_list = await submenu_crud.get_list(menu_id, offset, limit)
            data_submenu_list = [SubmenuResponse.model_validate(submenu) for submenu in submenu_list]
            await self.cache.set_all('submenu_list', data_submenu_list)
        return data_submenu_list

    async def update_submenu(
            self, menu_id: UUID, submenu_id: UUID, submenu_body: dict[str, str], back_tasks: BackgroundTasks
    ) -> SubmenuResponse | Exception:
        submenu_crud = SubmenuDAL(self.session)
        submenu = await submenu_crud.get(menu_id, submenu_id)
        if submenu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='submenu not found',
            )
        submenu_updated = await submenu_crud.update(
            menu_id, submenu_id, submenu_body
        )
        data_submenu_updated = SubmenuResponse.model_validate(submenu_updated)
        await self.cache.set_key(f'submenu_{submenu_id}', data_submenu_updated)
        back_tasks.add_task(self.cache.delete_cache, 'submenu_list')
        return data_submenu_updated

    async def delete_submenu(
            self, menu_id: UUID, submenu_id: UUID, back_tasks: BackgroundTasks
    ) -> UUID | Exception:
        submenu_crud = SubmenuDAL(self.session)
        submenu_deleted_id = await submenu_crud.delete(menu_id, submenu_id)
        if submenu_deleted_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='submenu not found',
            )
        back_tasks.add_task(self.cache.delete_cache, f'submenu_{submenu_deleted_id}')
        back_tasks.add_task(self.cache.delete_cache, f'menu_{menu_id}')
        back_tasks.add_task(self.cache.delete_cache, 'menu_list')
        back_tasks.add_task(self.cache.delete_cache, 'submenu_list')
        back_tasks.add_task(self.cache.delete_cache, 'dish_list')
        back_tasks.add_task(self.cache.delete_cache, 'full_menus_submenus_dishes')
        return submenu_deleted_id


def get_submenu_service(
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        redis_cache: RedisDB = Depends(get_redis)
) -> SubmenuService:
    return SubmenuService(session, cache=redis_cache)
