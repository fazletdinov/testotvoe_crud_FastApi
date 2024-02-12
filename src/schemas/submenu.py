from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .dish import DishResponse


class SubmenuResponse(BaseModel):
    id: UUID
    title: str
    description: str

    dishes_count: int

    model_config = ConfigDict(
        from_attributes=True, revalidate_instances='always'
    )


class SubmenuFullResponse(BaseModel):
    id: UUID
    title: str
    description: str

    dishes: list[DishResponse]

    model_config = ConfigDict(
        from_attributes=True, revalidate_instances='always'
    )


class SubmenuCreate(BaseModel):
    title: str
    description: str


class SubmenuUpdate(BaseModel):
    title: str | None
    description: str | None
