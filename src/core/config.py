from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

BASE_DIR = Path(__name__).parent.parent.parent


class AppSettings(BaseSettings):
    project_name: str = "Тестовое Y_LAB"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="db_", env_file=BASE_DIR / ".env"
    )
    name: str
    user: str
    password: SecretStr
    port: int
    host: str
    echo: bool = False

    def _url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:"
            f"{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def async_url(self) -> str:
        return self._url()


class DatabaseTestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="test_db_", env_file=BASE_DIR / ".env"
    )
    name: str
    user: str
    password: SecretStr
    port: int
    host: str
    echo: bool = True

    API_V1_STR: str = "http://127.0.0.1:8000"

    def _url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:"
            f"{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def async_url(self) -> str:
        return self._url()


class Settings:
    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    db_test: DatabaseTestSettings = DatabaseTestSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
