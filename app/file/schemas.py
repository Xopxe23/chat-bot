import datetime
import uuid

from app.common.schemas import OrmModel


class FileSchema(OrmModel):
    id: uuid.UUID
    filename: str
    content_type: str
    size: int
    url: str
    created_at: datetime.datetime
