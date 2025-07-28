from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository
from app.database.pg_client import get_db
from app.file.models import File
from app.file.schemas import FileSchema


class FileRepository(BaseRepository[File, FileSchema]):
    model = File
    schema = FileSchema


def get_file_repository(
        session: Annotated[AsyncSession, Depends(get_db)],
) -> FileRepository:
    return FileRepository(session)
