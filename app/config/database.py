from typing import Optional

from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    # TEST_POSTGRES_DB: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    @property
    def POSTGRES_URL(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    # @property
    # def TEST_DB_URL(self):
    #     return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
    #             f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.TEST_POSTGRES_DB}")

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def QDRANT_URL(self) -> str:
        return f"http://{self.host}:{self.port}"

    class Config:
        env_file = ".env"
        extra = "allow"
