import datetime
import uuid

from sqlalchemy import UUID, TIMESTAMP, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class BaseModelMixin:
    @declared_attr
    def id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
