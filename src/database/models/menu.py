from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped, column_property
from sqlalchemy import select, func

from src.database.models.base import Base

if TYPE_CHECKING:
    from .submenu import Submenu
    from .dish import Dish


class Menu(Base):
    title: Mapped[str]
    description: Mapped[str]

    submenus: Mapped[list["Submenu"]] = relationship(
        back_populates="menu", cascade="all, delete", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"Menu: ({self.id} - {self.title})"


Menu.submenus_count = column_property(
    select(func.count(Submenu.id))
    .where(Menu.id == Submenu.menu_id)
    .correlate_except(Submenu)
    .scalar_subquery()
)

Menu.dishes_count = column_property(
    select(func.count(Dish.id))
    .join(Submenu)
    .where(Menu.id == Submenu.menu_id and Submenu.id == Dish.submenu_id)
    .correlate_except(Dish)
    .scalar_subquery()
)
