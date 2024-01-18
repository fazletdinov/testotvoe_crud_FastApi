import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey

from src.database.models.base import Base

if TYPE_CHECKING:
    from .dish import Dish
    from .menu import Menu


class Submenu(Base):
    title: Mapped[str]
    description: Mapped[str]

    menu_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("menu.id", ondelete="CASCADE")
    )
    menu: Mapped["Menu"] = relationship(back_populates="submenus")

    dishs: Mapped[list["Dish"]] = relationship(
        back_populates="submenu", cascade="all, delete", passive_deletes=True
    )
