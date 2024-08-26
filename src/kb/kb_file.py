import logging
import os

from fastapi import APIRouter, BackgroundTasks, Path, UploadFile, File
from fastapi.responses import FileResponse

from common import success, BaseResponse
from kb.file.file_service import check_file_size, check_file_type, save_file, get_upload_file_path
from kb.kb_config import DocxSchema
from kb.kb_core import get_kb_by_id
from kb.kb_loader import DocxLoader

router = APIRouter(prefix="/file",
                   tags=["Knowledge File"])
logger = logging.getLogger(__name__)


@router.put("/{kb_id}",
            summary="知识库上传",
            description="上传文档并且嵌入指定知识库，返回文档id", )
async def upload_file(background_tasks: BackgroundTasks,
                      kb_id: str = Path(..., examples=["Hello;bge-m3"], description="知识库id"),
                      file: UploadFile = File(..., description="知识库文件，当前仅支持docx")) -> BaseResponse:
    """
    文件上传接口
    """
    byte = await file.read()
    check_file_type(byte, file.filename)
    check_file_size(byte)
    file_id, save_path = save_file(byte, file.filename)
    background_tasks.add_task(write_to_kb_with_docx,
                              filepath=save_path,
                              kb_id=kb_id,
                              filename=file.filename,
                              file_id=file_id)
    return success(msg=f'{file.filename} upload success', data=file_id)


def write_to_kb_with_docx(filepath: str, kb_id: str, filename: str, file_id: str):
    """docx文档写入知识库"""
    loader = DocxLoader(file_path=filepath)
    loader.root.value = filename
    kb = get_kb_by_id(kb_id)
    for doc in loader.lazy_load():
        doc.metadata[DocxSchema.FILE_ID] = file_id
        kb.add_kb_split(doc)
    logger.info(f"Finish the doc-[{filename}] embed to kb-[{kb_id}]")
    return kb_id


@router.get('/file/{file_id}',
            summary="文档下载",
            description="通过上传时返回的文件id，将上传的文档下载")
async def get_doc(file_id: str = Path(..., description="文件路径")):
    file_path = get_upload_file_path(file_id=file_id)
    return FileResponse(path=file_path, filename=os.path.basename(file_path))
