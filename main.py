import uvicorn
from fastapi import FastAPI, APIRouter

from src.core.config import get_settings
from src.api.v1_handlers.dish import dish_router
from src.api.v1_handlers.menu import menu_router
from src.api.v1_handlers.submenu import submenu_router

app = FastAPI(title=get_settings().app.project_name)

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(dish_router)
main_router.include_router(menu_router)
main_router.include_router(submenu_router)

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
