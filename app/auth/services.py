from typing import Annotated

from fastapi import Depends
from jose import jwt

from app.auth.repositories import (
    AuthUserRepository,
    AuthVerifyCodeRepository,
    get_user_repository,
    get_verify_code_repository,
)
from app.auth.schemas import AuthUserSchema
from app.config.main import settings


class AuthService:
    def __init__(
            self,
            user_repo: AuthUserRepository,
            code_repo: AuthVerifyCodeRepository,
    ):
        self.user_repo = user_repo
        self.code_repo = code_repo

    @staticmethod
    def create_access_token(user: AuthUserSchema) -> str | None:
        data = {"sub": user.id.__str__()}
        to_encode = data.copy()
        encoded_jwt = jwt.encode(to_encode, settings.security.SECRET, algorithm=settings.security.ALGORITHM)
        return encoded_jwt


def get_auth_service(
    user_repo: Annotated[AuthUserRepository, Depends(get_user_repository)],
    code_repo: Annotated[AuthVerifyCodeRepository, Depends(get_verify_code_repository)],
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        code_repo=code_repo,
    )
