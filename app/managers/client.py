import httpx

from app.config.main import settings

http_client = httpx.AsyncClient(
    base_url=settings.security.OPENAI_URL,
    timeout=30.0,
    headers={
        "Authorization": f"Bearer {settings.security.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    },
)


def get_http_client():
    return http_client
