from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DishCreate(BaseModel):
    title: str
    description: str
    price: str


class DishUpdate(BaseModel):
    title: str | None
    description: str | None
    price: str | None


class DishResponse(BaseModel):
    id: UUID
    title: str
    description: str
    price: str

    model_config = ConfigDict(
        from_attributes=True, revalidate_instances="always"
    )
