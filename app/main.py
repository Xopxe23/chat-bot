import uvicorn
from fastapi import FastAPI

from app.chats.routers import router as chats_router

app = FastAPI()

app.include_router(chats_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", reload=True,
    )
