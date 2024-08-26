"""知识库API"""
import logging
from typing import Any

from fastapi import APIRouter, Path, Query, Body

import kb.kb_file
from common import success, failed
from kb.doc_retriever import get_doc_kb_by_id
from kb.kb_config import DocxSchema
from kb.kb_core import get_kb_by_id

router = APIRouter(prefix="/kb",
                   tags=["Knowledge Base"])

router.include_router(kb.kb_file.router
                      )

logger = logging.getLogger(__name__)


@router.get("/{kb_id}",
            summary="知识库相似查询",
            description="指定知识库查询相关结果，当前支持\n - 数量限制\n - 指定文档\n - 使用父子关联查询")
async def query_kb(kb_id: str = Path(..., examples=["Hello;bge-m3"], description="知识库id"),
                   query: str = Query(..., examples=["Hello"], description="查询相关文档"),
                   docs: list[str] = Query(None, description="指定相关文档id，上传时返回，具体可见上传文档接口 "),
                   limit: int = Query(3, description="查询条数", ge=1),
                   relevant: bool = Query(False, description="是否使用关联父子文档")):
    """知识库的向是查寻"""
    docs = get_relevant_doc_from_kb(query, kb_id, limit, docs, relevant)
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
                    limit: int = Query(10, description="限制条数", ge=1),
                    offset: int = Query(0, description="偏移量", ge=0)):
    """知识库的条件查询"""
    docs = scroll_kb_with_filter(kb_id, condition, limit, offset)
    data = [vars(doc) for doc in docs]
    return success(msg=f"Filter from knowledge base {kb_id}", data=data)


@router.delete("/{kb_id}",
               summary="从知识库中删除文档",
               description="指定文档id（上传文档时生成）和知识库，从指定知识库中删除文档")
async def delete_doc(kb_id: str = Path(..., examples=["Hello;bge-m3"],
                                       description="知识库id"),
                     doc_ids: list[str] = Query(..., description="指定相关文档id，上传时返回，具体可见上传文档接口 ")):
    res = delete_doc_from_kb(kb_id=kb_id, doc_ids=doc_ids)
    return success("成功删除") if res else failed("删除失败")


def delete_doc_from_kb(kb_id: str, doc_ids: list[str]):
    kb = get_kb_by_id(kb_id=kb_id)
    res = kb.remove_kb_split(ids=doc_ids)
    return res


def scroll_kb_with_filter(kb_id: str, condition: dict[str, Any] = None, limit: int = 10, offset=0):
    """遍历检索知识库，可以按条件查询"""
    kb = get_kb_by_id(kb_id)
    return kb.filter_by(filter_condition=condition, limit=limit, offset=offset)


def get_relevant_doc_from_kb(query: str, kb_id: str, limit: int, docs: list[str] = None, relevant=False):
    """从知识库中获取相关文档片段"""
    if docs:
        filter_condition = {DocxSchema.FILE_ID: docs}
    else:
        filter_condition = None
    kb = get_kb_by_id(kb_id)
    if relevant:
        kb = get_doc_kb_by_id(kb_id=kb_id)
    res = kb.query_doc(query=query, limit=limit, filter_condition=filter_condition)
    return res
