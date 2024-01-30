from uuid import UUID
from typing_extensions import override
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, update, delete, Result, select, Row, func
from fastapi import HTTPException, status

from .base_classes import CrudeBase
from src.database.models.submenu import Submenu
from src.database.models.dish import Dish
from src.schemas.submenu import SubmenuCreate


class SubmenuDAL(CrudeBase):
    def __init__(self, session: AsyncSession):
        self.db_session = session

    @override
    async def create(
        self, menu_id: UUID, submenu_body: SubmenuCreate
    ) -> Submenu | Exception | None:
        try:
            submenu: Submenu = Submenu(
                title=submenu_body.title,
                description=submenu_body.description,
                menu_id=menu_id,
            )
            self.db_session.add(submenu)
            await self.db_session.commit()
            await self.db_session.refresh(submenu)
            return await self.get(menu_id, submenu.id)
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
    ) -> Row[tuple[Submenu, int]] | Exception | None:
        try:
            query = (
                select(
                    Submenu.id,
                    Submenu.title,
                    Submenu.description,
                    func.count(Dish.id.distinct()).label("dishes_count"),
                )
                .where(Submenu.menu_id == menu_id, Submenu.id == submenu_id)
                .select_from(Submenu)
                .outerjoin(Dish)
                .group_by(Submenu.id, Submenu.title, Submenu.description)
            )
            res: Result = await self.db_session.execute(query)
            submenu: Row[tuple[Submenu, int]] | None = res.fetchone()
            if submenu is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="submenu not found",
                )
            return submenu

        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при получении Submenu",
            )

    async def get_list(
        self, menu_id: UUID, offset: int, limit: int
    ) -> None | Exception | Sequence[Row[tuple[Submenu, int]]]:
        try:
            query = (
                select(
                    Submenu.id,
                    Submenu.title,
                    Submenu.description,
                    func.count(Dish.id.distinct()).label("dishes_count"),
                )
                .where(Submenu.menu_id == menu_id)
                .select_from(Submenu)
                .outerjoin(Dish)
                .group_by(Submenu.id, Submenu.title, Submenu.description)
                .offset(offset)
                .limit(limit)
            )
            res: Result = await self.db_session.execute(query)
            dish_list: Sequence[Row[tuple[Submenu, int]]] = res.all()
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
        self, menu_id: UUID, submenu_id: UUID, submenu_body: dict[str, str]
    ) -> Submenu | None | Exception:
        try:
            stmt = (
                update(Submenu)
                .where(Submenu.id == submenu_id, Submenu.menu_id == menu_id)
                .values(**submenu_body)
            )
            await self.db_session.execute(stmt)
            await self.db_session.commit()
            return await self.get(menu_id, submenu_id)
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
