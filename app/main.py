from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.auth.routers import router as auth_router
from app.chat.routers import router as chats_router
from app.file.routers import router as files_router
from app.managers.client import get_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client = get_http_client()
    await client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(chats_router)
app.include_router(auth_router)
app.include_router(files_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", reload=True,
    )
