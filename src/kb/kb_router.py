from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Path

from common import BaseResponse, success
from kb.file.file_service import (check_file_type,
                                  save_file,
                                  check_file_size)
from kb.kb_core import get_kb_by_id
from kb.kb_loader import DocxLoader

router = APIRouter(prefix="/kb",
                   tags=["Knowledge Base"]
                   )


@router.post("/upload/{kb_id}")
async def upload_file(background_tasks: BackgroundTasks,
                      kb_id: str = Path(..., example="Hello;bge-m3", description="知识库id"),
                      file: UploadFile = File(..., description="知识库文件，当前仅支持docx")) -> BaseResponse:
    """
    文件上传接口
    """
    byte = await file.read()
    check_file_type(byte, file.filename)
    check_file_size(byte)
    file_id, save_path = save_file(byte, file.filename)
    background_tasks.add_task(write_to_kb_with_docx, filepath=save_path, kb_id=kb_id)
    return success(msg=f'{file.filename} upload success', data=file_id)


def write_to_kb_with_docx(filepath: str, kb_id: str):
    loader = DocxLoader(file_path=filepath)
    kb = get_kb_by_id(kb_id)
    for doc in loader.lazy_load():
        kb.add_kb_split(doc)
    return kb_id
