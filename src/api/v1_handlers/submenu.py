from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Depends, Path, HTTPException, status

from src.schemas.submenu import SubmenuResponse, SubmenuCreate, SubmenuUpdate
from src.service.submenu import SubmenuService, get_submenu_service

submenu_router = APIRouter(tags=["Submenu"])


@submenu_router.get(
    "/menus/{menu_id}/submenus",
    response_model=list[SubmenuResponse],
)
async def get_submenus(
    menu_id: Annotated[UUID, Path()],
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 50,
    submenu_servie: SubmenuService = Depends(get_submenu_service),
) -> list[SubmenuResponse] | Exception | None:
    return await submenu_servie.get_submenus_list(menu_id, offset, limit)


@submenu_router.get(
    "/menus/{menu_id}/submenus/{submenu_id}",
    response_model=SubmenuResponse,
)
async def get_submenu(
    menu_id: Annotated[UUID, Path()],
    submenu_id: Annotated[UUID, Path()],
    submenu_service: SubmenuService = Depends(get_submenu_service),
) -> SubmenuResponse | Exception:
    return await submenu_service.get_submenu(menu_id, submenu_id)


@submenu_router.post(
    "/menus/{menu_id}/submenus/", response_model=SubmenuResponse
)
async def create_submenu(
    menu_id: Annotated[UUID, Path()],
    submenu: SubmenuCreate,
    submenu_service: SubmenuService = Depends(get_submenu_service),
) -> SubmenuResponse:
    return await submenu_service.create_submenu(menu_id, submenu)


@submenu_router.patch(
    "/menus/{menu_id}/submenus/{submenu_id}", response_model=SubmenuResponse
)
async def update_submenu(
    menu_id: Annotated[UUID, Path()],
    submenu_id: Annotated[UUID, Path()],
    submenu: SubmenuUpdate,
    submenu_service: SubmenuService = Depends(get_submenu_service),
) -> SubmenuResponse | Exception:
    submenu_update: dict[str, str] = submenu.model_dump(exclude_none=True)
    if submenu_update is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нужно заполнить хотябы одно поле",
        )
    return await submenu_service.update_submenu(
        menu_id, submenu_id, submenu_update
    )


@submenu_router.delete(
    "/menus/{menu_id}/submenus/{submenu_id}",
    response_model=dict[str, str | bool],
)
async def delete_submenu(
    menu_id: Annotated[UUID, Path()],
    submenu_id: Annotated[UUID, Path()],
    submenu_service: SubmenuService = Depends(get_submenu_service),
) -> dict[str, bool | str] | None:
    submenu_id_deleted = await submenu_service.delete_submenu(
        menu_id, submenu_id
    )
    if submenu_id_deleted is not None:
        return {"status": True, "message": "The submenu has been deleted"}
