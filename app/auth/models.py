import datetime
import random
import string
import uuid

from pydantic import EmailStr
from sqlalchemy import TIMESTAMP, UUID, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models import BaseModelMixin, CreatedAtMixin
from app.database.pg_client import Base


def generate_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_uppercase, k=length))


class AuthUser(Base, BaseModelMixin, CreatedAtMixin):
    __tablename__ = "auth_user"

    email: Mapped[EmailStr] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    verify_codes: Mapped[list["AuthVerifyCode"]] = relationship(
        "AuthVerifyCode",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class AuthVerifyCode(Base, BaseModelMixin):
    __tablename__ = "auth_verify_code"

    code: Mapped[str] = mapped_column(
        String(6),
        index=True,
        default=generate_code,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth_user.id"),
    )
    expired_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5),
        nullable=False,
    )

    user: Mapped["AuthUser"] = relationship(
        "AuthUser",
        back_populates="verify_codes"
    )
