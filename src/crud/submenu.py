from uuid import UUID
from typing import Any
from typing_extensions import override

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, update, delete, Result, select, ScalarResult
from fastapi import HTTPException, status

from .base_classes import CrudeBase
from src.database.models.submenu import Submenu
from src.schemas.submenu import SubmenuCreate, SubmenuResponse


class SubmenuDAL(CrudeBase):
    def __init__(self, session: AsyncSession):
        self.db_session = session

    @override
    async def create(
        self, menu_id: UUID, submenu_body: SubmenuCreate
    ) -> Submenu | Exception:
        try:
            submenu: Submenu = Submenu(
                title=submenu_body.title,
                description=submenu_body.description,
                menu_id=menu_id,
            )
            self.db_session.add(submenu)
            await self.db_session.commit()
            await self.db_session.refresh(submenu)
            return submenu
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при создании Submenu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при создании Submenu",
            )

    @override
    async def get(
        self, menu_id: UUID, submenu_id: UUID
    ) -> Submenu | Exception | None:
        try:
            query = select(Submenu).where(
                Submenu.menu_id == menu_id, Submenu.id == submenu_id
            )
            res: Result = await self.db_session.execute(query)
            submenu = res.scalar()
            return submenu
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при получении Submenu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при получении Submenu",
            )

    async def get_list(
        self, menu_id: UUID, offset: int, limit: int
    ) -> None | Exception | list[SubmenuResponse] | ScalarResult:
        try:
            query = (
                select(Submenu)
                .where(Submenu.menu_id == menu_id)
                .offset(offset)
                .limit(limit)
            )
            res: Result = await self.db_session.execute(query)
            dish_list = res.scalars()
            return dish_list
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при получении списка Submenu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при получении списка Submenu",
            )

    @override
    async def update(
        self, menu_id: UUID, submenu_id: UUID, submenu: dict[str, Any]
    ) -> Submenu | None | Exception:
        try:
            stmt = (
                update(Submenu)
                .where(Submenu.id == submenu_id, Submenu.menu_id == menu_id)
                .values(**submenu)
                .returning(Submenu.id)
            )
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            menu_id = res.scalar()
            menu = await self.db_session.get(Submenu, menu_id)
            return menu
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при обновлении Submenu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при обновлении Submenu",
            )

    @override
    async def delete(
        self, menu_id: UUID, submenu_id: UUID
    ) -> Exception | None | UUID:
        try:
            stmt = (
                delete(Submenu)
                .where(Submenu.id == submenu_id, Submenu.menu_id == menu_id)
                .returning(Submenu.id)
            )
            res = await self.db_session.execute(stmt)
            await self.db_session.commit()
            del_submenu_id = res.scalar()
            return del_submenu_id

        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при удалении Submenu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при удалении Submenu",
            )
