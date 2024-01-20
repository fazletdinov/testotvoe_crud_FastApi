from uuid import UUID
from typing import Any
from typing_extensions import override

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, update, delete, Result, select
from fastapi import HTTPException, status

from .base_classes import CrudeBase
from src.database.models.submenu import Submenu


class SubmenuDAL(CrudeBase):
    def __init__(self, session: AsyncSession):
        self.db_session = session

    @override
    async def create(
        self, title: str, description: str
    ) -> Submenu | Exception:
        try:
            submenu: Submenu = Submenu(title=title, description=description)
            self.db_session.add(submenu)
            await self.db_session.execute()
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
    async def get(self, submenu_id: UUID) -> Submenu | Exception | None:
        try:
            submenu = await self.db_session.get(Submenu, submenu_id)
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
        self, offset: int, limit: int
    ) -> None | Exception | Any:
        try:
            query = select(Submenu).offset(offset=offset).limit(limit=limit)
            res: Result = await self.db_session.execute(query)
            dish_list = res.fetchall()
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
        self, submenu_id: UUID, **kwargs: dict[Any, Any]
    ) -> UUID | None | Exception:
        try:
            stmt = (
                update(Submenu)
                .where(Submenu.id == submenu_id)
                .values(kwargs)
                .returning(Submenu)
            )
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            menu = res.fetchone()
            if menu is not None:
                return menu[0]
            return None
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
    async def delete(self, submenu: UUID) -> Exception | None | UUID:
        try:
            stmt = (
                delete(Submenu)
                .where(Submenu.id == submenu)
                .returning(Submenu.id)
            )
            res = await self.db_session.execute(stmt)
            await self.db_session.commit()
            del_submenu_id = res.fetchone()
            if del_submenu_id is not None:
                return del_submenu_id[0]
            return None

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
