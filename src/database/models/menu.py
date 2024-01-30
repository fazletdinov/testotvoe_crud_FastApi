from sqlalchemy.orm import relationship, Mapped

from src.database.models.base import Base
from src.database.models.submenu import Submenu


class Menu(Base):
    title: Mapped[str]
    description: Mapped[str]

    submenus: Mapped[list["Submenu"]] = relationship(
        back_populates="menu", cascade="all, delete", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"Menu: ({self.id} - {self.title})"


# Menu.submenus_count = column_property(
#     select(func.count(Submenu.id))
#     .where(Menu.id == Submenu.menu_id)
#     .correlate_except(Submenu)
#     .scalar_subquery()
# )
#
# Menu.dishes_count = column_property(
#     select(func.count(Dish.id))
#     .join(Submenu, Submenu.menu_id == Menu.id)
#     .where(Dish.submenu_id == Submenu.id)
#     .correlate_except(Submenu)
#     .scalar_subquery(),
# )
