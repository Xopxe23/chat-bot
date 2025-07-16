import datetime

from pydantic import EmailStr
from sqlalchemy import TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.models import BaseModelMixin
from app.database import Base


class Users(Base, BaseModelMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[EmailStr] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, default=datetime.datetime.now(datetime.UTC))
