from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    REDIS_URL: str

    KAFKA_HOST: str
    KAFKA_PORT: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
