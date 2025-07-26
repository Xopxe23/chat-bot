from app.config.database import DatabaseConfig
from app.config.security import SecurityConfig


class Settings:
    def __init__(self):
        self.database = DatabaseConfig()
        self.security = SecurityConfig()


settings = Settings()
