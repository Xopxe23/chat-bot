from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import AuthUser, AuthVerifyCode
from app.auth.schemas import AuthUserSchema, AuthVerifyCodeSchema
from app.common.repositories import BaseRepository
from app.database import get_db


class AuthUserRepository(BaseRepository[AuthUser, AuthUserSchema]):
    model = AuthUser
    schema = AuthUserSchema


def get_user_repository(
        session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthUserRepository:
    return AuthUserRepository(session)


class AuthVerifyCodeRepository(BaseRepository[AuthVerifyCode, AuthVerifyCodeSchema]):
    model = AuthVerifyCode
    schema = AuthVerifyCodeSchema


def get_verify_code_repository(
        session: Annotated[AsyncSession, Depends(get_db)],
) -> AuthVerifyCodeRepository:
    return AuthVerifyCodeRepository(session)
