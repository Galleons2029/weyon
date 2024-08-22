"""知识库API"""
import logging
from typing import Any

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Path, Query, Body

from common import BaseResponse, success
from kb.doc_retriever import get_doc_kb_by_id
from kb.file.file_service import (check_file_type,
                                  save_file,
                                  check_file_size)
from kb.kb_config import DocxMetadataConfig
from kb.kb_core import get_kb_by_id
from kb.kb_loader import DocxLoader

router = APIRouter(prefix="/kb",
                   tags=["Knowledge Base"])

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


@router.get("/{kb_id}",
            summary="知识库相似查询",
            description="指定知识库查询相关结果，当前支持\n - 数量限制\n - 指定文档\n - 使用父子关联查询")
async def query_kb(kb_id: str = Path(..., examples=["Hello;bge-m3"], description="知识库id"),
                   query: str = Query(..., examples=["Hello"], description="查询相关文档"),
                   docs: list[str] = Query(None, description="指定相关文档id，上传时返回，具体可见上传文档接口 "),
                   limit: int = Query(3, description="查询条数"),
                   relevant: bool = Query(False, description="是否使用关联父子文档")):
    """知识库的向是查寻"""
    docs = get_rel_docs_from_kb(query, kb_id, limit, docs, relevant)
    data = [vars(doc) for doc in docs]
    return success(msg=f"Query [{query}] has found some relative documents", data=data)


@router.post("/{kb_id}",
             summary="知识库条件查询",
             description="筛选查询知识库中的数据")
async def filter_kb(kb_id: str = Path(..., examples=["Hello;bge-m3"],
                                      description="知识库id"),
                    condition: dict[str, list[str]] = Body(None,
                                                           description="过滤条件，前面为元数据中的键，后买了为匹配的值。"
                                                                       "\n最终条件为(key1.value in (targets1) and key2.value in (targets2))"),
                    limit: int = Query(10, description="限制条数"),
                    offset: int = Query(0, description="偏移量")):
    """知识库的条件查询"""
    docs = scroll_kb_with_filter(kb_id, condition, limit, offset)
    data = [vars(doc) for doc in docs]
    return success(msg=f"Filter from knowledge base {kb_id}", data=data)


def scroll_kb_with_filter(kb_id: str, condition: dict[str, Any] = None, limit: int = 10, offset=0):
    """遍历检索知识库，可以按条件查询"""
    kb = get_kb_by_id(kb_id)
    return kb.filter_by(filter_condition=condition, limit=limit, offset=offset)


def get_rel_docs_from_kb(query: str, kb_id: str, limit: int, docs: list[str] = None, relevant=False):
    """从知识库中获取相关文档片段"""
    if docs:
        filter_condition = {DocxMetadataConfig.FILE_ID: docs}
    else:
        filter_condition = None
    kb = get_kb_by_id(kb_id)
    if relevant:
        kb = get_doc_kb_by_id(kb_id)
    res = kb.query_doc(query=query, limit=limit, filter_condition=filter_condition)
    return res


def write_to_kb_with_docx(filepath: str, kb_id: str, filename: str, file_id: str):
    """docx文档写入知识库"""
    loader = DocxLoader(file_path=filepath)
    loader.root.value = filename
    kb = get_kb_by_id(kb_id)
    for doc in loader.lazy_load():
        doc.metadata[DocxMetadataConfig.FILE_ID] = file_id
        kb.add_kb_split(doc)
    logger.info(f"Finish the doc-[{filename}] embed to kb-[{kb_id}]")
    return kb_id
