from typing import List

from qdrant_client.models import models

from kb.kb_config import DocxMetadataConfig
from kb.kb_core import Document, VectorKB, KnowledgeBase


class DocRetriever(KnowledgeBase):

    def add_kb_split(self, doc: Document):
        self.vector_kb.add_kb_split(doc)

    def query_doc(self, query: str, filter_condition=None, limit=3, *args, **kwargs) -> list[Document]:
        chunks = self.vector_kb.query_doc(query=query, filter_condition=filter_condition, limit=limit * 3, *args,
                                          **kwargs)
        doc_rel = self._remove_duplicates(chunk.metadata.get(DocxMetadataConfig.PARENT_ID) for chunk in chunks)
        docs = self._get_docs_by_parent(doc_rel)
        self._resort_doc(docs)
        docs = self._merge_doc(docs)
        return docs[:limit]

    def __init__(self, vector_kb: VectorKB):
        self.vector_kb = vector_kb

    @staticmethod
    def merge_with_common_prefix(str1, str2):
        # 找到两个字符串的公共前缀
        common = ""
        for c1, c2 in zip(str1, str2):
            if c1 == c2:
                common += c1
            else:
                break
        # 合并字符串，只保留一份公共前缀
        merged = common + str1[len(common):] + '\n' + str2[len(common):]
        return merged

    @staticmethod
    def _remove_duplicates(lst):
        return list(set(lst))

    def _get_docs_by_parent(self, doc_rel: List[List[str]]) -> List[Document]:
        """通过父节点id查找响嘎un节点"""
        # langchain中的qdrant无法执行scroll操作，因此需要调用qdrant的python客户端
        fil = models.Filter(
            should=[
                models.FieldCondition(key=f'{DocxMetadataConfig.METADATA}.{DocxMetadataConfig.PARENT_ID}',
                                      match=models.MatchAny(any=doc_rel))]
        )
        recs = self.vector_kb.scroll(scroll_filter=fil)
        return [Document(page_content=chunk.payload[DocxMetadataConfig.PAGE_CONTENT],
                         metadata=chunk.payload[DocxMetadataConfig.METADATA]) for
                chunk in recs[0]]

    @staticmethod
    def _resort_doc(docs: List[Document]):
        """文档重新排序"""
        docs.sort(key=lambda x: x.metadata[DocxMetadataConfig.ORDER_BY])

    def _merge_doc(self, docs: List[Document]) -> List[Document]:
        """合并相同父节点的文档"""
        pre_doc: Document | None = None
        parent_id = None
        for doc in docs:
            if doc.metadata[DocxMetadataConfig.PARENT_ID] != parent_id:
                parent_id = doc.metadata[DocxMetadataConfig.PARENT_ID]
                pre_doc = doc
            else:
                pre_doc.page_content = self.merge_with_common_prefix(pre_doc.page_content, doc.page_content)
                doc.page_content = ""

        docs = [doc for doc in docs if doc.page_content != ""]
        return docs


def get_doc_kb_by_id(kb_id: str):
    from kb.kb_core import __kb_register, get_kb_by_id
    vkb = get_kb_by_id(kb_id)
    key = f'{kb_id};doc'
    if key not in __kb_register:
        __kb_register[key] = DocRetriever(vkb)
    return get_kb_by_id(key)
