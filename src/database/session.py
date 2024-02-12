from asyncio import current_task
from dataclasses import dataclass
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
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

    async def scoped_session_dependency(self):
        scoped_factory = async_scoped_session(
            self.async_session,
            scopefunc=current_task,
        )
        try:
            async with scoped_factory() as session:
                yield session
        finally:
            await scoped_factory.remove()


db_helper: DatabaseHelper = DatabaseHelper(
    url=settings.db.async_url, echo=settings.db.echo
)
