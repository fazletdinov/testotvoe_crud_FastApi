from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped

from src.database.models.base import Base

if TYPE_CHECKING:
    from .submenu import Submenu


class Menu(Base):
    title: Mapped[str]
    description: Mapped[str]

    submenus: Mapped[list["Submenu"]] = relationship(
        back_populates="menu", cascade="all, delete", passive_deletes=True
    )
