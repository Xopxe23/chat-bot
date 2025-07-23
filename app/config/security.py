from pydantic_settings import BaseSettings


class SecurityConfig(BaseSettings):
    SECRET: str
    ALGORITHM: str

    class Config:
        env_file = ".env"
        extra = "allow"
