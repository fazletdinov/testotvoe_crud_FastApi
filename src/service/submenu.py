from abc import ABCMeta, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends

from src.crud.submenu import SubmenuDAL
from src.schemas.submenu import SubmenuResponse, SubmenuCreate
from src.database.session import db_helper


class SubmenuServiceBase(metaclass=ABCMeta):
    @abstractmethod
    async def create_submenu(self, *args: Any) -> Any:
        pass

    @abstractmethod
    async def get_submenu(self, *args: Any) -> Any:
        pass

    @abstractmethod
    async def get_submenus_list(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def update_submenu(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def delete_submenu(self, *args: Any) -> Any:
        pass


class SubmenuService(SubmenuServiceBase):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_submenu(
        self, menu_id: UUID, submenu_body: SubmenuCreate
    ) -> SubmenuResponse:
        submenu_crud = SubmenuDAL(self.session)
        submenu = await submenu_crud.create(menu_id, submenu_body)
        return SubmenuResponse.model_validate(submenu)

    async def get_submenu(
        self, menu_id: UUID, submenu_id: UUID
    ) -> SubmenuResponse | Exception:
        submenu_crud = SubmenuDAL(self.session)
        submenu = await submenu_crud.get(menu_id, submenu_id)
        if submenu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="submenu not found",
            )
        return SubmenuResponse.model_validate(submenu)

    async def get_submenus_list(
        self, menu_id: UUID, offset: int, limit: int
    ) -> list[SubmenuResponse] | Exception | None:
        submenu_crud = SubmenuDAL(self.session)
        submenu_list = await submenu_crud.get_list(menu_id, offset, limit)
        return submenu_list

    async def update_submenu(
        self, menu_id: UUID, submenu_id: UUID, submenu_body: dict[str, str]
    ) -> SubmenuResponse | Exception:
        submenu_crud = SubmenuDAL(self.session)
        submenu = await submenu_crud.get(menu_id, submenu_id)
        if submenu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="submenu not found",
            )
        submenu_updated = await submenu_crud.update(
            menu_id, submenu_id, submenu_body
        )
        return SubmenuResponse.model_validate(submenu_updated)

    async def delete_submenu(
        self, menu_id: UUID, submenu_id: UUID
    ) -> UUID | Exception:
        submenu_crud = SubmenuDAL(self.session)
        submenu_deleted_id = await submenu_crud.delete(menu_id, submenu_id)
        if submenu_deleted_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="submenu not found",
            )
        return submenu_deleted_id


def get_submenu_service(
    session: AsyncSession = Depends(db_helper.get_scoped_session),
) -> SubmenuService:
    return SubmenuService(session)
