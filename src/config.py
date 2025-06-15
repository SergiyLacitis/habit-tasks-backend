from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class AppConfig(BaseModel):
    reload: bool
    host: str
    port: int


class DatabaseConfig(BaseModel):
    echo: bool
    echo_pool: bool
    pool_size: int
    max_overflow: int
    engine: str
    host: str
    port: int
    user: str
    password: str
    name: str


class Settings(BaseSettings):
    app: AppConfig
    database: DatabaseConfig
    model_config = SettingsConfigDict(toml_file=("config.toml"))

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


settings = Settings()
