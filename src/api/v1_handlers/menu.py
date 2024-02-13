from typing import Annotated
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
from sqlalchemy import ScalarResult

from src.schemas.menu import (
    MenuCreate,
    MenuResponse,
    MenuSubmenuDishResponse,
    MenuUpdate,
)
from src.service.menu import MenuService, get_menu_service

menu_router = APIRouter(tags=['Menu'])


@menu_router.get('/menus/', response_model=list[MenuResponse])
async def get_menus(
        offset: Annotated[int, Query()] = 0,
        limit: Annotated[int, Query()] = 50,
        menu_service: MenuService = Depends(get_menu_service),
) -> None | Exception | ScalarResult | list[MenuResponse]:
    return await menu_service.get_menus_list(offset, limit)


@menu_router.get('/menus/{menu_id}/', response_model=MenuResponse)
async def get_menu(
        menu_id: Annotated[UUID, Path()],
        menu_service: MenuService = Depends(get_menu_service),
) -> MenuResponse | Exception:
    return await menu_service.get_menu(menu_id)


@menu_router.post(
    '/menus/', response_model=MenuResponse, status_code=status.HTTP_201_CREATED
)
async def create_menu(
        back_tasks: BackgroundTasks,
        body: MenuCreate, menu_service: MenuService = Depends(get_menu_service),
) -> MenuResponse | Exception:
    return await menu_service.create_menu(body, back_tasks)


@menu_router.patch('/menus/{menu_id}/', response_model=MenuResponse)
async def update_menu(
        menu_id: Annotated[UUID, Path()],
        body: MenuUpdate,
        back_tasks: BackgroundTasks,
        menu_service: MenuService = Depends(get_menu_service),
) -> MenuResponse | Exception:
    menu_body: dict[str, str] = body.model_dump(exclude_none=True)
    if menu_body is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Для обновления нужно ввести хотябы одно поле',
        )
    return await menu_service.update_menu(menu_id, menu_body, back_tasks)


@menu_router.delete(
    '/menus/{menu_id}/',
    response_model=dict[str, str | bool],
)
async def delete_menu(
        menu_id: Annotated[UUID, Path()],
        back_tasks: BackgroundTasks,
        menu_service: MenuService = Depends(get_menu_service),
) -> dict[str, str | bool] | Exception | None:
    menu_deleted_id = await menu_service.delete_menu(menu_id, back_tasks)
    if menu_deleted_id is not None:
        return {'status': True, 'message': 'The menu has been deleted'}
    return None


@menu_router.get('/full_menus_submenus_dishes/', response_model=list[MenuSubmenuDishResponse])
async def get_full_menus_submenus_dishes(
        offset: Annotated[int, Query()] = 0,
        limit: Annotated[int, Query()] = 50,
        menu_service: MenuService = Depends(get_menu_service)):
    return await menu_service.full_menus_submenus_dishes(offset, limit)
