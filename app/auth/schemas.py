import datetime
import uuid

from pydantic import BaseModel, EmailStr

from app.common.schemas import OrmModel


class EmailSchema(BaseModel):
    email: EmailStr


class SendCodeSchema(EmailSchema):
    pass


class VerifyCodeSchema(EmailSchema):
    code: str


class AuthUserSchema(OrmModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    created_at: datetime.datetime


class AuthVerifyCodeSchema(OrmModel):
    user_id: uuid.UUID
    code: str
    expired_at: datetime.datetime
