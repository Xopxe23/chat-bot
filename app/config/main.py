from app.config.pg import PostgresConfig
from app.config.security import SecurityConfig


class Settings:
    def __init__(self):
        self.postgres = PostgresConfig()
        self.security = SecurityConfig()


settings = Settings()
