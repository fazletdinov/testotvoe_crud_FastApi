from typing import Annotated, Any
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)

from src.schemas.dish import DishCreate, DishResponse, DishUpdate
from src.service.dish import DishService, get_dish_service

dish_router = APIRouter(tags=['Dish'])


@dish_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/',
    response_model=list[DishResponse],
)
async def get_dishes(
    submenu_id: Annotated[UUID, Path()],
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 50,
    dish_service: DishService = Depends(get_dish_service),
) -> list[DishResponse] | None | Exception | Any:
    return await dish_service.get_dish_list(submenu_id, offset, limit)


@dish_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}/',
    response_model=DishResponse,
)
async def get_dish(
    submenu_id: Annotated[UUID, Path()],
    dish_id: Annotated[UUID, Path()],
    dish_service: DishService = Depends(get_dish_service),
) -> DishResponse | Exception:
    return await dish_service.get_dish(submenu_id, dish_id)


@dish_router.post(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/',
    response_model=DishResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dish(
    menu_id: Annotated[UUID, Path()],
    submenu_id: Annotated[UUID, Path()],
    dish_body: DishCreate,
    back_tasks: BackgroundTasks,
    dish_service: DishService = Depends(get_dish_service),
) -> DishResponse:
    return await dish_service.create_dish(menu_id, submenu_id, dish_body, back_tasks)


@dish_router.patch(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}/',
    response_model=DishResponse,
)
async def update_dish(
    submenu_id: Annotated[UUID, Path()],
    dish_id: Annotated[UUID, Path()],
    dish_body: DishUpdate,
    back_tasks: BackgroundTasks,
    dish_service: DishService = Depends(get_dish_service),
) -> DishResponse | Exception:
    dish: dict[str, str] = dish_body.model_dump(exclude_none=True)
    if dish is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Нужно заполнить хотябы одно поле',
        )
    return await dish_service.update_dish(submenu_id, dish_id, dish, back_tasks)


@dish_router.delete(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}/',
    response_model=dict[str, str | bool],
)
async def delete_dish(
    menu_id: Annotated[UUID, Path()],
    submenu_id: Annotated[UUID, Path()],
    dish_id: Annotated[UUID, Path()],
    back_tasks: BackgroundTasks,
    dish_service: DishService = Depends(get_dish_service),
) -> dict[str, str | bool] | None:
    dish_deleted_id = await dish_service.delete_dish(menu_id, submenu_id, dish_id, back_tasks)
    if dish_deleted_id is not None:
        return {'status': True, 'message': 'The dish has been deleted'}
    return None
