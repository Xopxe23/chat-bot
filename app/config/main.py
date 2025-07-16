from pydantic_settings import BaseSettings

from app.config.pg import PostgresConfig


class Settings:
    def __init__(self):
        self.postgres = PostgresConfig()


settings = Settings()
