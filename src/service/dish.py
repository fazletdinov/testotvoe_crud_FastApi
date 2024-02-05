from abc import ABCMeta, abstractmethod
from typing import Any
from uuid import UUID

from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.dish import DishDAL
from src.database.redis_cache import RedisDB, get_redis
from src.database.session import db_helper
from src.schemas.dish import DishCreate, DishResponse


class DishServiceBase(metaclass=ABCMeta):
    @abstractmethod
    async def create_dish(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get_dish(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get_dish_list(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def update_dish(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def delete_dish(self, *args: Any, **kwargs: Any) -> Any:
        pass


class DishService(DishServiceBase):
    def __init__(self, session: AsyncSession, cache: RedisDB) -> None:
        self.session = session
        self.cache = cache

    async def create_dish(
        self, menu_id: UUID, submenu_id: UUID, dish_body: DishCreate, back_tasks: BackgroundTasks
    ) -> DishResponse:
        dish_crud = DishDAL(self.session)
        dish = await dish_crud.create(submenu_id, dish_body)
        back_tasks.add_task(self.cache.delete_cache, 'menu_list')
        back_tasks.add_task(self.cache.delete_cache, 'submenu_list')
        back_tasks.add_task(self.cache.delete_cache, 'dish_list')
        back_tasks.add_task(self.cache.delete_cache, f'submenu_{submenu_id}')
        back_tasks.add_task(self.cache.delete_cache, f'menu_{menu_id}')
        return DishResponse.model_validate(dish)

    async def get_dish(
        self, submenu_id: UUID, dish_id: UUID
    ) -> DishResponse | Exception:
        cache_dish = await self.cache.get_value(f'dish_{dish_id}')
        if cache_dish:
            data_dish = cache_dish
        else:
            dish_crud = DishDAL(self.session)
            dish = await dish_crud.get(submenu_id, dish_id)
            if dish is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='dish not found'
                )
            data_dish = DishResponse.model_validate(dish)
            await self.cache.set_key(f'dish_{dish_id}', data_dish)
        return data_dish

    async def get_dish_list(
        self, submenu_id: UUID, offset: int, limit: int
    ) -> list[DishResponse]:
        cache_dish_list = await self.cache.get_value('dish_list')
        if cache_dish_list:
            data_dish_list = cache_dish_list
        else:
            dish_crud = DishDAL(self.session)
            dish_list = await dish_crud.get_list(submenu_id, offset, limit)
            data_dish_list = [DishResponse.model_validate(dish) for dish in dish_list]
            await self.cache.set_all('dish_list', data_dish_list)
        return data_dish_list

    async def update_dish(
        self, submenu_id: UUID, dish_id: UUID, dish_body: dict[str, str], back_tasks: BackgroundTasks
    ) -> DishResponse | Exception:
        dish_crud = DishDAL(self.session)
        dish = await dish_crud.get(submenu_id, dish_id)
        if dish is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='dish not found'
            )
        dish_updated = await dish_crud.update(submenu_id, dish_id, dish_body)
        data_dish_updated = DishResponse.model_validate(dish_updated)
        await self.cache.set_key(f'dish_{dish_id}', data_dish_updated)
        back_tasks.add_task(self.cache.delete_cache, 'dish_list')
        return data_dish_updated

    async def delete_dish(
        self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, back_tasks: BackgroundTasks
    ) -> Exception | None | UUID:
        dish_crud = DishDAL(self.session)
        dish = await dish_crud.get(submenu_id, dish_id)
        if dish is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='dish not found'
            )
        dish_deleted_id = await dish_crud.delete(submenu_id, dish_id)
        back_tasks.add_task(self.cache.delete_cache, f'menu_{menu_id}')
        back_tasks.add_task(self.cache.delete_cache, f'submenu_{submenu_id}')
        back_tasks.add_task(self.cache.delete_cache, f'dish_{dish_id}')
        back_tasks.add_task(self.cache.delete_cache, 'menu_list')
        back_tasks.add_task(self.cache.delete_cache, 'submenu_list')
        back_tasks.add_task(self.cache.delete_cache, 'dish_list')
        return dish_deleted_id


def get_dish_service(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    redis_cache: RedisDB = Depends(get_redis)
) -> DishService:
    return DishService(session, cache=redis_cache)
