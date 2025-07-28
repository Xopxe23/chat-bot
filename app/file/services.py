import uuid
from typing import Annotated

import httpx
from botocore.client import BaseClient
from fastapi import Depends, UploadFile

from app.config.main import settings
from app.database.s3_client import get_s3_client
from app.file.repositories import FileRepository, get_file_repository
from app.file.schemas import FileSchema
from app.managers.client import get_http_client


class FileService:
    def __init__(
            self,
            file_repo: FileRepository,
            s3_repo: BaseClient,
            client: httpx.AsyncClient,
    ):
        self.file_repo = file_repo
        self.s3_repo = s3_repo
        self.client = client

    async def upload_file(
            self,
            file: UploadFile,
    ) -> FileSchema:
        file_id = uuid.uuid4()
        s3_key = f"uploads/{str(file_id)}_{file.filename}"
        async with self.s3_repo as s3_client:
            await s3_client.upload_fileobj(
                Fileobj=file.file,
                Bucket=settings.database.MINIO_BUCKET_NAME,
                Key=s3_key,
                ExtraArgs={"ContentType": file.content_type},
            )
        url = f"{settings.database.MINIO_URL}/{settings.database.MINIO_BUCKET_NAME}/{s3_key}"
        file_data = await self.file_repo.add(
            id=file_id,
            filename=file.filename,
            size=file.size,
            content_type=file.content_type,
            url=url,
        )
        return file_data


def get_file_service(
        file_repo: Annotated[FileRepository, Depends(get_file_repository)],
        s3_repo: Annotated[BaseClient, Depends(get_s3_client)],
        client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> FileService:
    return FileService(file_repo, s3_repo, client)
