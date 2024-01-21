import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped, mapped_column, column_property
from sqlalchemy import ForeignKey, func, select, UUID

from src.database.models.base import Base
from src.database.models.dish import Dish

if TYPE_CHECKING:
    from .menu import Menu


class Submenu(Base):
    title: Mapped[str]
    description: Mapped[str]

    menu_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("menu.id", ondelete="CASCADE")
    )
    menu: Mapped["Menu"] = relationship(back_populates="submenus")

    dishes: Mapped[list["Dish"]] = relationship(
        back_populates="submenu", cascade="all, delete", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"Submenu: ({self.id} - {self.title})"


Submenu.dishes_count = column_property(
    select(func.count(Dish.id))
    .where(Submenu.id == Dish.submenu_id)
    .correlate_except(Dish)
    .scalar_subquery()
)
