from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MenuCreate(BaseModel):
    title: str
    description: str


class MenuUpdate(BaseModel):
    title: str | None
    description: str | None


class MenuResponse(BaseModel):
    id: UUID
    title: str
    description: str

    submenus_count: int
    dishes_count: int

    model_config = ConfigDict(
        from_attributes=True, revalidate_instances="always"
    )
