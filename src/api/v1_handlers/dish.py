from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Depends, Path, HTTPException, status
from sqlalchemy import ScalarResult

from src.schemas.dish import DishResponse, DishCreate, DishUpdate
from src.service.dish import DishService, get_dish_service

dish_router = APIRouter(tags=["Dish"])


@dish_router.get(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes",
    response_model=list[DishResponse],
)
async def get_dishes(
    submenu_id: Annotated[UUID, Path()],
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 50,
    dish_service: DishService = Depends(get_dish_service),
) -> None | Exception | list[DishResponse] | ScalarResult:
    return await dish_service.get_dish_list(submenu_id, offset, limit)


@dish_router.get(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=DishResponse | Exception,
)
async def get_dish(
    submenu_id: Annotated[UUID, Path()],
    dish_id: Annotated[UUID, Path()],
    dish_service: DishService = Depends(get_dish_service),
) -> DishResponse | Exception:
    return await dish_service.get_dish(submenu_id, dish_id)


@dish_router.post(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes/",
    response_model=DishResponse,
)
async def create_dish(
    submenu_id: Annotated[UUID, Path()],
    dish_body: DishCreate,
    dish_service: DishService = Depends(get_dish_service),
) -> DishResponse:
    return await dish_service.create_dish(submenu_id, dish_body)


@dish_router.patch(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=DishResponse | Exception,
)
async def update_dish(
    submenu_id: Annotated[UUID, Path()],
    dish_id: Annotated[UUID, Path()],
    dish_body: DishUpdate,
    dish_service: DishService = Depends(get_dish_service),
) -> DishResponse | Exception:
    dish: dict[str, str] = dish_body.model_dump(exclude_none=True)
    if dish is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нужно заполнить хотябы одно поле",
        )
    return await dish_service.update_dish(submenu_id, dish_id, dish)


@dish_router.delete(
    "/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=dict[str, str | bool] | None,
)
async def delete_dish(
    submenu_id: Annotated[UUID, Path()],
    dish_id: Annotated[UUID, Path()],
    dish_service: DishService = Depends(get_dish_service),
) -> dict[str, str | bool] | None:
    dish_deleted_id = await dish_service.delete_dish(submenu_id, dish_id)
    if dish_deleted_id is not None:
        return {"status": True, "message": "The dish has been deleted"}
    return None
