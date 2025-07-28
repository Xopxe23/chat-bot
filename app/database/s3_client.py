from contextlib import asynccontextmanager

import aioboto3

from app.config.main import settings


@asynccontextmanager
async def get_s3_client():
    session = aioboto3.Session()
    async with session.client(
        "s3",
        aws_access_key_id=settings.database.MINIO_USER,
        aws_secret_access_key=settings.database.MINIO_PASSWORD,
        endpoint_url=settings.database.MINIO_URL,
        region_name="us-east-1",
    ) as client:
        yield client
