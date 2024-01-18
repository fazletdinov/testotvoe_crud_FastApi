import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey

from src.database.models.base import Base

if TYPE_CHECKING:
    from .submenu import Submenu


class Dish(Base):
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[str]

    submenu_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "submenu.id",
            ondelete="CASCADE",
        )
    )
    submenu: Mapped["Submenu"] = relationship(back_populates="dishs")
