from typing import AsyncGenerator, Any
from dataclasses import dataclass
from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
    async_scoped_session,
)

from src.core.config import get_settings


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

    def get_scoped_session(self) -> Any:
        session = async_scoped_session(
            session_factory=self.async_session, scopefunc=current_task
        )
        return session

    async def scoped_session_dependency(
        self,
    ) -> AsyncGenerator[AsyncSession, None]:
        session = self.get_scoped_session()
        yield session
        await session.close()


db_helper: DatabaseHelper = DatabaseHelper(
    url=get_settings().db.async_url, echo=get_settings().db.echo
)
