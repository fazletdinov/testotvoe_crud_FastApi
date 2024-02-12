from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__name__).parent.parent.parent


class AppSettings(BaseSettings):
    project_name: str = 'Тестовое Y_LAB'


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='db_', env_file=BASE_DIR / '.env'
    )
    name: str
    user: str
    password: SecretStr
    port: int
    host: str
    echo: bool = False

    def _url(self) -> str:
        return (
            f'postgresql+asyncpg://{self.user}:'
            f'{self.password.get_secret_value()}'
            f'@{self.host}:{self.port}/{self.name}'
        )

    @property
    def async_url(self) -> str:
        return self._url()


class DatabaseTestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='test_db_', env_file=BASE_DIR / '.env'
    )
    name: str
    user: str
    password: SecretStr
    port: int
    host: str
    echo: bool = True

    API_V1_STR: str = 'http://127.0.0.1:8006/api/v1'

    def _url(self) -> str:
        return (
            f'postgresql+asyncpg://{self.user}:'
            f'{self.password.get_secret_value()}'
            f'@{self.host}:{self.port}/{self.name}'
        )

    @property
    def async_url(self) -> str:
        return self._url()


class RedisSettings(BaseSettings):
    host: str
    port: int
    password: SecretStr
    expire_in_sec: int

    def _url(self) -> str:
        return (
            f'redis://:{self.password.get_secret_value()}@{self.host}:{self.port}/0'
        )

    @property
    def backend_url(self) -> str:
        return self._url()

    model_config = SettingsConfigDict(env_prefix='redis_', env_file=BASE_DIR / '.env')


class RabbitmqSettings(BaseSettings):
    host: str
    user: str
    port1: int
    port2: int
    hostname: str
    password: SecretStr
    vhost: str

    def _url(self) -> str:
        return (
            f'amqp://{self.user}:{self.password.get_secret_value()}@'
            f'{self.host}:{self.port1}/{self.vhost}'
        )

    @property
    def broker_url(self) -> str:
        return self._url()

    model_config = SettingsConfigDict(env_prefix='rabbitmq_', env_file=BASE_DIR / '.env')


class RedisTestSettings(BaseSettings):
    host: str
    port: int
    password: SecretStr
    expire_in_sec: int

    model_config = SettingsConfigDict(env_prefix='test_redis_', env_file=BASE_DIR / '.env')


class Settings:
    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    db_test: DatabaseTestSettings = DatabaseTestSettings()
    redis: RedisSettings = RedisSettings()
    redis_test: RedisTestSettings = RedisTestSettings()
    rabbitmq: RabbitmqSettings = RabbitmqSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
