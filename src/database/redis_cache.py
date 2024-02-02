from abc import ABCMeta, abstractmethod
from typing import Any

import backoff
from aioredis.client import Redis
from aioredis.exceptions import BusyLoadingError, ConnectionError, TimeoutError
from fastapi import Depends

from src.core.config import Settings, get_settings


class RedisDBBase(metaclass=ABCMeta):

    @abstractmethod
    async def set_value(self, *args: Any) -> Any:
        pass

    @abstractmethod
    async def get_value(self, *args: Any) -> Any:
        pass

    @abstractmethod
    async def is_exists(self, *args: Any) -> Any:
        pass


class RedisDB(RedisDBBase):
    def __init__(self, host: str, port: int, password: str, expire_in_sec: int) -> None:
        self.expire_in_sec = expire_in_sec
        self.redis = Redis(host=host, port=port, password=password)

    @backoff.on_exception(backoff.expo,
                          (BusyLoadingError, ConnectionError, TimeoutError),
                          max_tries=5,
                          raise_on_giveup=True)
    async def set_value(self, key: str, value: Any) -> None:
        await self.redis.set(key, value, self.expire_in_sec)

    @backoff.on_exception(backoff.expo,
                          (BusyLoadingError, ConnectionError, TimeoutError),
                          max_tries=5,
                          raise_on_giveup=True)
    async def is_exists(self, key: str) -> bool:
        return await self.redis.exists(key)

    @backoff.on_exception(backoff.expo,
                          (BusyLoadingError, ConnectionError, TimeoutError),
                          max_tries=5,
                          raise_on_giveup=True)
    async def get_value(self, key: str) -> Any:
        return await self.redis.get(key)


@backoff.on_exception(backoff.expo, ConnectionError, max_tries=5, raise_on_giveup=True)
async def get_redis(settings: Settings = Depends(get_settings)) -> RedisDBBase:
    return RedisDB(host=settings.redis.host,
                   port=settings.redis.port,
                   password=settings.redis.password.get_secret_value(),
                   expire_in_sec=settings.redis.expire_in_sec)
