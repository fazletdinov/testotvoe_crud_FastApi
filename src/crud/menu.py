from typing import Any, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Result, Row, delete, exc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing_extensions import override

from src.database.models.dish import Dish
from src.database.models.menu import Menu
from src.database.models.submenu import Submenu
from src.schemas.menu import MenuCreate

from .base_classes import CrudeBase


class MenuDAL(CrudeBase):
    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    @override
    async def create(self, body: MenuCreate) -> Menu | Exception | Any:
        try:
            new_menu = Menu(title=body.title,
                            description=body.description)
            self.db_session.add(new_menu)
            await self.db_session.commit()
            await self.db_session.refresh(new_menu)
            return await self.get(new_menu.id)
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Ошибка SqlalchemyError при создании Menu',
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Неизвестная ошибка при создании Menu',
            )

    @override
    async def get(
            self, menu_id: UUID
    ) -> Row[tuple[Menu, int, int]] | Exception | None:
        try:
            query = (
                select(
                    Menu.id,
                    Menu.title,
                    Menu.description,
                    func.count(Submenu.id.distinct()).label('submenus_count'),
                    func.count(Dish.id.distinct()).label('dishes_count'),
                )
                .where(Menu.id == menu_id)
                .select_from(Menu)
                .outerjoin(Submenu)
                .outerjoin(Dish)
                .group_by(Menu.id, Menu.title, Menu.description)
            )
            res: Result = await self.db_session.execute(query)
            menu_info: Row[tuple[Menu, int, int]] | None = res.fetchone()
            return menu_info

        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Ошибка SQLAlchemyError при получение Menu',
            )

    async def get_list(
            self, offset: int, limit: int
    ) -> Sequence[Row[tuple[Menu, int, int]]]:
        try:
            query = (
                select(
                    Menu.id,
                    Menu.title,
                    Menu.description,
                    func.count(Submenu.id.distinct()).label('submenus_count'),
                    func.count(Dish.id.distinct()).label('dishes_count'),
                )
                .select_from(Menu)
                .outerjoin(Submenu, Menu.id == Submenu.menu_id)
                .outerjoin(Dish, Submenu.id == Dish.submenu_id)
                .group_by(Menu.id, Menu.title, Menu.description)
                .offset(offset=offset)
                .limit(limit=limit)
            )
            res: Result = await self.db_session.execute(query)
            menu_list = res.all()
            return menu_list

        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Ошибка SqlalchemyError при получении списка Menu',
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Неизвестная ошибка при получении списка Menu',
            )

    @override
    async def update(
            self, menu_id: UUID, body: dict[str, str]
    ) -> Menu | Exception | None:
        try:
            stmt = update(Menu).where(Menu.id == menu_id).values(**body)
            await self.db_session.execute(stmt)
            await self.db_session.commit()
            menu = await self.get(menu_id)
            return menu

        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Ошибка SQLAlchemyError при обновлении Menu',
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Неизвестная ошибка при обновлении Menu',
            )

    @override
    async def delete(self, menu_id: UUID) -> Exception | None | UUID:
        try:
            stmt = delete(Menu).where(Menu.id == menu_id).returning(Menu.id)
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            menu_id = res.scalar()
            return menu_id

        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Ошибка SQLAlchemyError при удалении Menu',
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Неизвестная ошибка при удалении Menu',
            )

    async def get_full_menus_submenus_dishes(
            self, offset: int, limit: int
    ) -> Sequence[Row[tuple[Menu, int, int]]]:
        try:
            query = (
                select(Menu
                       )
                .options(selectinload(Menu.submenus).selectinload(Submenu.dishes))
                .offset(offset=offset)
                .limit(limit=limit)
            )
            res: Result = await self.db_session.execute(query)
            menu_list = res.scalars().all()
            return menu_list

        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Ошибка SqlalchemyError при получении списка Menu, Submenu, Dish',
            )
