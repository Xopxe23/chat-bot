from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.models import BaseModelMixin, CreatedAtMixin
from app.database.pg_client import Base


class File(Base, BaseModelMixin, CreatedAtMixin):
    __tablename__ = "file"

    filename: Mapped[str] = mapped_column(String(256))
    content_type: Mapped[str] = mapped_column(String(256))
    size: Mapped[int]
    url: Mapped[str] = mapped_column(String(512))
