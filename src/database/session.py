from typing import AsyncGenerator
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)
from src.core.config import settings


@dataclass()
class DatabaseHelper:
    url: str
    echo: bool

    def __post_init__(self) -> None:
        self.engine = create_async_engine(url=self.url, echo=self.echo)
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
        )

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session() as session:
            yield session


helper: DatabaseHelper = DatabaseHelper(
    url=settings.db.async_url, echo=settings.db.echo
)
