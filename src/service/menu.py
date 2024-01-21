from abc import ABCMeta, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
from sqlalchemy import ScalarResult

from src.crud.menu import MenuDAL
from src.database.session import db_helper
from src.schemas.menu import MenuResponse


class MenuServiceBase(metaclass=ABCMeta):
    @abstractmethod
    async def create_menu(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get_menu(self, *args: Any) -> Any:
        pass

    @abstractmethod
    async def get_menus_list(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def update_menu(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def delete_menu(self, *args: Any) -> Any:
        pass


class MenuService(MenuServiceBase):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_menu(self, body: dict[str, str]) -> MenuResponse:
        menu_crud = MenuDAL(self.session)
        menu = await menu_crud.create(body)
        return MenuResponse.model_validate(menu)

    async def get_menu(self, menu_id: UUID) -> MenuResponse | Exception:
        menu_crud = MenuDAL(self.session)
        menu = await menu_crud.get(menu_id)
        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="menu not found"
            )
        return MenuResponse.model_validate(menu)

    async def get_menus_list(
        self, offset: int, limit: int
    ) -> None | Exception | ScalarResult | list[MenuResponse]:
        menu_crud = MenuDAL(self.session)
        menu_list = await menu_crud.get_list(offset, limit)
        return menu_list

    async def update_menu(
        self, menu_id: UUID, body: dict[str, Any]
    ) -> MenuResponse | Exception:
        menu_crud = MenuDAL(self.session)
        menu = await menu_crud.get(menu_id)
        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="menu not found"
            )
        menu_updated = await menu_crud.update(menu_id, body)
        return MenuResponse.model_validate(menu_updated)

    async def delete_menu(self, menu_id: UUID) -> Exception | None | UUID:
        menu_crud = MenuDAL(self.session)
        menu_delete_id = await menu_crud.delete(menu_id)
        return menu_delete_id


def get_menu_service(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> MenuService:
    return MenuService(session)
