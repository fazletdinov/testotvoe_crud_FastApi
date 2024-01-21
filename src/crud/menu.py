from uuid import UUID
from typing import Any
from typing_extensions import override

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, update, delete, Result, select, ScalarResult
from fastapi import HTTPException, status

from .base_classes import CrudeBase
from src.database.models.menu import Menu
from src.schemas.menu import MenuResponse


class MenuDAL(CrudeBase):
    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    @override
    async def create(self, body: dict[str, Any]) -> Menu | Exception:
        try:
            new_menu = Menu(**body)
            self.db_session.add(new_menu)
            await self.db_session.commit()
            await self.db_session.refresh(new_menu)
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
    async def get(self, menu_id: UUID) -> MenuResponse | None | Exception:
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
    ) -> None | Exception | ScalarResult | list[MenuResponse]:
        try:
            query = select(Menu).offset(offset=offset).limit(limit=limit)
            res: Result = await self.db_session.execute(query)
            dish_list = res.scalars()
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
        self, menu_id: UUID, body: dict[str, Any]
    ) -> Menu | Exception | None:
        try:
            stmt = (
                update(Menu)
                .where(Menu.id == menu_id)
                .values(**body)
                .returning(Menu.id)
            )
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            menu_id = res.scalar()
            menu = await self.db_session.get(Menu, menu_id)
            return menu

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
    async def delete(self, menu_id: UUID) -> Exception | None | UUID:
        try:
            stmt = delete(Menu).where(Menu.id == menu_id).returning(Menu.id)
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            menu = res.scalar()
            return menu

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
