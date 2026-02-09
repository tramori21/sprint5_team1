from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    elastic_host: str = "http://elasticsearch:9200"
    redis_host: str = "redis"
    redis_port: int = 6379


settings = Settings()
