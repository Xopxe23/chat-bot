import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.auth.repositories import (
    AuthUserRepository,
    AuthVerifyCodeRepository,
    get_user_repository,
    get_verify_code_repository,
)
from app.auth.schemas import SendCodeSchema, VerifyCodeSchema
from app.auth.services import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["Users"])


@router.post("/send-code", response_model=dict)
async def send_code(
        data: SendCodeSchema,
        user_repo: Annotated[AuthUserRepository, Depends(get_user_repository)],
        verify_code_repo: Annotated[AuthVerifyCodeRepository, Depends(get_verify_code_repository)],
):
    try:
        user = await user_repo.get_one(email=data.email)
    except ValueError:
        user = await user_repo.add(**data.model_dump())
    try:
        code = await verify_code_repo.add(
            user_id=user.id,
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {"status": f"verify code sent on email {code.code}"}


@router.post("/verify-code", response_model=dict)
async def verify_code(
        data: VerifyCodeSchema,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        user = await auth_service.user_repo.get_one(email=data.email)
    except ValueError:
        raise HTTPException(status_code=400, detail="Email not found")
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        _ = await auth_service.code_repo.get_one(
            user_id=user.id,
            code=data.code,
            expired_at__gt=now,
        )
        token = auth_service.create_access_token(user)
    except ValueError:
        raise HTTPException(status_code=401, detail="Wrong code")
    return {"token": token}
