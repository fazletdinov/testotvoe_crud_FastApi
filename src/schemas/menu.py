from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MenuCreate(BaseModel):
    title: str
    description: str


class MenuResponse(BaseModel):
    id: UUID
    title: str
    description: str

    submenus_count: int = 0
    dishes_count: int = 0

    model_config = ConfigDict(from_attributes=True)
