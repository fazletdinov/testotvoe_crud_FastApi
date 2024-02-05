from abc import ABCMeta, abstractmethod
from typing import Any


class CrudeBase(metaclass=ABCMeta):
    @abstractmethod
    async def create(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def get(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def update(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    async def delete(self, *args: Any, **kwargs: Any) -> Any:
        pass
