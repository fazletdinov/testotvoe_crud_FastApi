from abc import ABCMeta, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
from sqlalchemy import ScalarResult

from src.crud.dish import DishDAL
from src.database.session import db_helper
from src.schemas.dish import DishResponse, DishCreate


class DishServiceBase(metaclass=ABCMeta):
    @abstractmethod
    async def create_dish(self, *args: Any) -> Any:
        pass

    @abstractmethod
    async def get_dish(self, *args: Any) -> Any:
        pass

    @abstractmethod
    async def get_dish_list(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def update_dish(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def delete_dish(self, *args: Any) -> Any:
        pass


class DishService(DishServiceBase):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_dish(
        self, submenu_id: UUID, dish_body: DishCreate
    ) -> DishResponse:
        dish_crud = DishDAL(self.session)
        dish = await dish_crud.create(submenu_id, dish_body)
        return DishResponse.model_validate(dish)

    async def get_dish(
        self, submenu_id: UUID, dish_id: UUID
    ) -> DishResponse | Exception:
        dish_crud = DishDAL(self.session)
        dish = await dish_crud.get(submenu_id, dish_id)
        if dish is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="dish not found"
            )
        return DishResponse.model_validate(dish)

    async def get_dish_list(
        self, submenu_id: UUID, offset: int, limit: int
    ) -> None | Exception | list[DishResponse] | ScalarResult:
        dish_crud = DishDAL(self.session)
        dish_list = await dish_crud.get_list(submenu_id, offset, limit)
        return dish_list

    async def update_dish(
        self, submenu_id: UUID, dish_id: UUID, dish_body: dict[str, str]
    ) -> DishResponse | Exception:
        dish_crud = DishDAL(self.session)
        dish = await dish_crud.get(submenu_id, dish_id)
        if dish is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="dish not found"
            )
        dish_updated = await dish_crud.update(submenu_id, dish_id, dish_body)
        return DishResponse.model_validate(dish_updated)

    async def delete_dish(
        self, submenu_id: UUID, dish_id: UUID
    ) -> Exception | None | UUID:
        dish_crud = DishDAL(self.session)
        dish_deleted_id = await dish_crud.delete(submenu_id, dish_id)
        return dish_deleted_id


def get_dish_service(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> DishService:
    return DishService(session)
