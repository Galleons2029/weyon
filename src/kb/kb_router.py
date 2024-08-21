from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Path, Query

from common import BaseResponse, success
from kb.doc_retriever import get_doc_kb_by_id
from kb.file.file_service import (check_file_type,
                                  save_file,
                                  check_file_size)
from kb.kb_core import get_kb_by_id
from kb.kb_loader import DocxLoader

router = APIRouter(prefix="/kb",
                   tags=["Knowledge Base"]
                   )


@router.put("/{kb_id}",
            summary="知识库上传",
            description="上传文档并且嵌入指定知识库")
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
    background_tasks.add_task(write_to_kb_with_docx, filepath=save_path, kb_id=kb_id, filename=file.filename)
    return success(msg=f'{file.filename} upload success', data=file_id)


@router.get("/{kb_id}",
            summary="知识库查询",
            description="指定知识库查询相关结果，当前支持\n - 数量限制\n - 指定文档\n - 使用父子关联查询")
async def query_kb(kb_id: str = Path(..., example="Hello;bge-m3", description="知识库id"),
                   query: str = Query(..., example="Hello", description="查询相关文档"),
                   docs: list[str] = Query(None, description="指定相关文档"),
                   limit: int = Query(3, description="查询条数"),
                   relevant: bool = Query(False, description="是否使用关联父子文档")):
    docs = get_rel_docs(query, kb_id, limit, docs, relevant)
    data = [vars(doc) for doc in docs]
    return success(msg=f"Query [{query}] has found some relative documents", data=data)


def get_rel_docs(query: str, kb_id: str, limit: int, docs: list[str] = None, relevant=False):
    if docs:
        filter_condition = {'doc': docs}
    else:
        filter_condition = None
    kb = get_kb_by_id(kb_id)
    if relevant:
        kb = get_doc_kb_by_id(kb_id)
    res = kb.query_doc(query, limit=limit, filter_condition=filter_condition)
    return res


def write_to_kb_with_docx(filepath: str, kb_id: str, filename: str):
    loader = DocxLoader(file_path=filepath)
    loader.root.value = filename
    kb = get_kb_by_id(kb_id)
    for doc in loader.lazy_load():
        kb.add_kb_split(doc)
    return kb_id
