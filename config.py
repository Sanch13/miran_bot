from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_TELEGRAM_TOKEN: SecretStr
    DATABASE: str
    CHANNEL_LINK: str
    CHANNEL_ID_MIRAN: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
