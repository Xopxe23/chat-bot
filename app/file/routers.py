from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette import status

from app.file.services import FileService, get_file_service

router = APIRouter(prefix="/file", tags=["Files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    service: FileService = Depends(get_file_service),
):
    try:
        result = await service.upload_file(file)
        return {"message": "Файл успешно загружен", "file": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
