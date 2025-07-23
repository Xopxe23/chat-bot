from pydantic_settings import BaseSettings


class SecurityConfig(BaseSettings):
    SECRET: str
    ALGORITHM: str
    OPENAI_URL: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "allow"
