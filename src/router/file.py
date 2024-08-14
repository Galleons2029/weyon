import magic
from fastapi import APIRouter, UploadFile, File, HTTPException

from common.base_response import BaseResponse

router = APIRouter(prefix="/files",
                   tags=["files"]
                   )

# 允许的 MIME 类型
ALLOWED_MIME_TYPES = {
    "image/jpeg": ["jpg", "jpeg"],
    "image/png": ["png"],
}

# 创建一个 magic.Magic 对象，使用 mime 真类来检测 MIME 类型
mime = magic.Magic(mime=True)


@router.post("/file/upload/")
async def upload_file(file: UploadFile = File(...)) -> BaseResponse:
    """
    文件上传接口
    param file: 上传的文件
    return: 返回文件id
    """
    # 读取文件内容以确定 MIME 类型
    file_mime_type = mime.from_buffer(await file.read())

    # 检查 MIME 类型是否被允许
    if file_mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File MIME type not allowed")

    # 检查文件扩展名是否与 MIME 类型匹配
    file_extension = file.filename.split('.')[-1].lower()
    if not any(file_extension in extensions for extensions in ALLOWED_MIME_TYPES.values()):
        raise HTTPException(status_code=400, detail="File extension does not match MIME type")

    return BaseResponse.success(msg=f'{file.filename} upload success')
