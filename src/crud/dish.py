from uuid import UUID
from typing import Any
from typing_extensions import override

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, update, delete, Result, select
from fastapi import HTTPException, status

from .base_classes import CrudeBase
from src.database.models.dish import Dish


class DishDAL(CrudeBase):
    def __int__(self, session: AsyncSession) -> None:
        self.db_session = session

    @override
    async def create(self, title: str, description: str) -> Dish | Exception:
        try:
            dish = Dish(title=title, description=description)
            self.db_session.add(dish)
            await self.db_session.commit()
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
    async def get(self, dish_id: UUID) -> Dish | None | Exception:
        try:
            dish = await self.db_session.get(Dish, dish_id)
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
        self, offset: int, limit: int
    ) -> None | Exception | Any:
        try:
            query = select(Dish).offset(offset=offset).limit(limit=limit)
            res: Result = await self.db_session.execute(query)
            dish_list = res.fetchall()
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
        self, dish_id: UUID, **kwargs: dict[Any, Any]
    ) -> Dish | Exception | None:
        try:
            stmt = update(Dish).where(Dish.id == dish_id).returning(Dish)
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            dish = res.fetchone()
            if dish is not None:
                return dish[0]
            return None
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
    async def delete(self, dish_id: UUID) -> Exception | None | UUID:
        try:
            stmt = delete(Dish).where(Dish.id == dish_id).returning(Dish.id)
            res: Result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            del_dish_id = res.fetchone()
            if del_dish_id is not None:
                return del_dish_id[0]
            return None
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
