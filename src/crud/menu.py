from uuid import UUID
from typing import Any
from typing_extensions import override

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, update, delete, Result, select
from fastapi import HTTPException, status

from .base_classes import CrudeBase
from src.database.models.menu import Menu


class MenuDAL(CrudeBase):
    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    @override
    async def create(self, title: str, description: str) -> Menu | Exception:
        try:
            new_menu = Menu(title=title, description=description)
            self.db_session.add(new_menu)
            await self.db_session.commit()
            return new_menu
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при создании Menu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при создании Menu",
            )

    @override
    async def get(self, menu_id: UUID) -> Menu | None | Exception:
        try:
            menu = await self.db_session.get(Menu, menu_id)
            return menu
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SQLAlchemyError при получение Menu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при получение Menu",
            )

    async def get_list(
        self, offset: int, limit: int
    ) -> None | Exception | Any:
        try:
            query = select(Menu).offset(offset=offset).limit(limit=limit)
            res: Result = await self.db_session.execute(query)
            dish_list = res.fetchall()
            return dish_list
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при получении списка Menu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при получении списка Menu",
            )

    @override
    async def update(
        self, menu_id: UUID, **kwargs: dict[Any, Any]
    ) -> Menu | Exception | None:
        try:
            stmt = (
                update(Menu)
                .where(Menu.id == menu_id)
                .values(kwargs)
                .returning(Menu)
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
                detail="Ошибка SQLAlchemyError при обновлении Menu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при обновлении Menu",
            )

    @override
    async def delete(self, menu_id: UUID) -> Exception | None | Any:
        try:
            stmt = delete(Menu).where(Menu.id == menu_id).returning(Menu.id)
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            menu_id = res.scalar()
            return menu_id

        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SQLAlchemyError при удалении Menu",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при удалении Menu",
            )
