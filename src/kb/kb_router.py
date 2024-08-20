from fastapi import APIRouter, UploadFile, File

from common import BaseResponse, success
from kb.file.file_service import (check_file_type,
                                  save_file,
                                  check_file_size)

router = APIRouter(prefix="/kb",
                   tags=["Knowledge Base"]
                   )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> BaseResponse:
    """
    文件上传接口
    """
    # 读取文件内容
    byte = await file.read()
    check_file_type(byte, file.filename)
    check_file_size(byte)
    file_id = save_file(byte, file.filename)
    return success(msg=f'{file.filename} upload success', data=file_id)
