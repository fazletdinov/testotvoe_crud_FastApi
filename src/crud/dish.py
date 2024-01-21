from uuid import UUID
from typing_extensions import override

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, update, delete, Result, select, ScalarResult
from fastapi import HTTPException, status

from .base_classes import CrudeBase
from src.database.models.dish import Dish
from src.schemas.dish import DishCreate, DishResponse


class DishDAL(CrudeBase):
    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    @override
    async def create(
        self, submenu_id: UUID, dish_body: DishCreate
    ) -> Dish | Exception:
        try:
            dish = Dish(
                title=dish_body.title,
                description=dish_body.description,
                price=dish_body.price,
                submenu_id=submenu_id,
            )
            self.db_session.add(dish)
            await self.db_session.commit()
            await self.db_session.refresh(dish)
            return dish
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при создании Dish",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при создании Dish",
            )

    @override
    async def get(
        self, submenu_id: UUID, dish_id: UUID
    ) -> Dish | None | Exception:
        try:
            query = select(Dish).where(
                Dish.id == dish_id, Dish.submenu_id == submenu_id
            )
            res: Result = await self.db_session.execute(query)
            dish = res.scalar()
            return dish
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при получении Dish",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при получении Dish",
            )

    async def get_list(
        self, submenu_id: UUID, offset: int, limit: int
    ) -> None | Exception | list[DishResponse] | ScalarResult:
        try:
            query = (
                select(Dish)
                .where(Dish.submenu_id == submenu_id)
                .offset(offset)
                .limit(limit)
            )
            res: Result = await self.db_session.execute(query)
            dish_list = res.scalars()
            return dish_list
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при получении списка Dish",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при получении списка Dish",
            )

    @override
    async def update(
        self, submenu_id: UUID, dish_id: UUID, dish_body: dict[str, str]
    ) -> Dish | Exception | None:
        try:
            stmt = (
                update(Dish)
                .where(Dish.id == dish_id, Dish.submenu_id == submenu_id)
                .values(**dish_body)
                .returning(Dish.id)
            )
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            dish_id = res.scalar()
            dish = await self.db_session.get(Dish, dish_id)
            return dish
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при обновлении Dish",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при обновлении Dish",
            )

    @override
    async def delete(
        self, submenu_id: UUID, dish_id: UUID
    ) -> Exception | None | UUID:
        try:
            stmt = (
                delete(Dish)
                .where(Dish.id == dish_id, Dish.submenu_id == submenu_id)
                .returning(Dish.id)
            )
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            del_dish_id = res.scalar()
            return del_dish_id
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка SqlalchemyError при удалении Dish",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Неизвестная ошибка при удалении Dish",
            )
