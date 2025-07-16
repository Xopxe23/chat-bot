import uvicorn
from fastapi import FastAPI

from app.chat.routers import router as chats_router
from app.auth.routers import router as auth_router

app = FastAPI()

app.include_router(chats_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", reload=True,
    )
