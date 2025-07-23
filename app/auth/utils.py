from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.auth.repositories import AuthUserRepository, get_user_repository
from app.auth.schemas import AuthUserSchema
from app.config.main import settings


def parse_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.security.SECRET, algorithms=[settings.security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    return {
        "sub": user_id,
    }


security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    auth_db: AuthUserRepository = Depends(get_user_repository),
) -> AuthUserSchema | None:
    token = credentials.credentials
    token_data = parse_token(token)
    if not token_data:
        return None
    user_id = token_data.get("sub")
    if not user_id:
        return None
    user = await auth_db.get_one(id=user_id)
    return user
