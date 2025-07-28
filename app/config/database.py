from typing import Optional

from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = 'postgres'
    # TEST_POSTGRES_DB: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    MINIO_USER: str = 'minioadmin'
    MINIO_PASSWORD: str = 'minioadmin'
    MINIO_HOST: str = 'localhost'
    MINIO_PORT: int = 9000
    MINIO_BUCKET_NAME: str = 'minio'

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

    @property
    def MINIO_URL(self) -> str:
        return f"http://{self.MINIO_HOST}:{self.MINIO_PORT}"

    class Config:
        env_file = ".env"
        extra = "allow"
