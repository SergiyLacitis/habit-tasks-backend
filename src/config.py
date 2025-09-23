from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

BASE_DIR = Path(__file__).parent


class AppSettings(BaseModel):
    reload: bool = False
    host: str = "0.0.0.0"
    port: int = 8000


class AuthSettings(BaseModel):
    secret_key_path: str = (BASE_DIR / "certs" / "jwt" / "private.pem").read_text()
    public_key_path: str = (BASE_DIR / "certs" / "jwt" / "public.pem").read_text()
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30


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
    auth: AuthSettings = Field(default_factory=AuthSettings)
    model_config = SettingsConfigDict(
        toml_file=BASE_DIR / "config.toml",
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
