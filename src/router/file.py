import os.path
import uuid

import magic
from fastapi import APIRouter, UploadFile, File, HTTPException

from common.base_response import BaseResponse, success
from config import UploadConfig

router = APIRouter(prefix="/files",
                   tags=["files"]
                   )

# 创建一个 magic.Magic 对象，使用 mime 真类来检测 MIME 类型
mime = magic.Magic(mime=True)


def check_file_type(byte, filename):
    """检查文件类型在指定类型范围内"""
    # 以确定 MIME 类型
    file_mime_type = mime.from_buffer(byte)

    # 检查 MIME 类型是否被允许
    if file_mime_type not in UploadConfig.ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File MIME type not allowed")

    # 检查文件扩展名是否与 MIME 类型匹配
    file_extension = filename.split('.')[-1].lower()
    if not any(file_extension in extensions for extensions in UploadConfig.ALLOWED_MIME_TYPES.values()):
        raise HTTPException(status_code=400, detail="File extension does not match MIME type")


def check_file_size(byte):
    """检查文件大小不得超出指定大小"""
    limit_size = UploadConfig.MAX_FILE_SIZE * 1024 * 1024
    if len(byte) > limit_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size limited in {UploadConfig.MAX_FILE_SIZE}MB"
        )


def save_file(contents, filename) -> str:
    """
    保存文件到配置目录
    :param contents: 文件内容
    :param filename: 上传时的文件名
    :return: 文件id
    """
    file_id = uuid.uuid4().__str__()
    os.makedirs(UploadConfig.UPLOAD_SAVING_PATH, exist_ok=True)
    save_file_path = os.path.join(UploadConfig.UPLOAD_SAVING_PATH, file_id + '.' + filename.split('.')[-1].lower())
    print(f'File will be saved in {save_file_path}')
    with open(save_file_path, 'wb') as f:
        f.write(contents)
    return file_id


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)) -> BaseResponse:
    """
    文件上传接口
    param file: 上传的文件
    return: 返回文件id
    """
    # 读取文件内容
    byte = await file.read()
    check_file_type(byte, file.filename)
    check_file_size(byte)
    file_id = save_file(byte, file.filename)
    return success(msg=f'{file.filename} upload success', data=file_id)
