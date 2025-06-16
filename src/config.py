from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class AppSettings(BaseModel):
    reload: bool = False
    host: str = "localhost"
    port: int = 8000


class DatabseEngineSettings(BaseModel):
    name: str
    echo: bool
    echo_pool: bool
    pool_size: int
    max_overflow: int


class DatabaseNamingConventionsSettings(BaseModel):
    ix: str = "ix_%(column_0_label)s"
    uq: str = "uq_%(table_name)s_%(column_0_name)s"
    ck: str = "ck_%(table_name)s_`%(constraint_name)s`"
    fk: str = "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
    pk: str = "pk_%(table_name)s"


class DatabaseSettings(BaseModel):
    engine: DatabseEngineSettings
    naming_conventions: DatabaseNamingConventionsSettings = Field(
        default_factory=DatabaseNamingConventionsSettings
    )
    host: str
    port: int
    user: str
    password: str
    name: str


class Settings(BaseSettings):
    app: AppSettings
    database: DatabaseSettings
    model_config = SettingsConfigDict(
        toml_file=["config.toml"],
    )

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


settings = Settings()  # pyright: ignore[reportCallIssue]
