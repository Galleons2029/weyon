"""
知识库注册中心，负责管理知识库的注册和知识库和向量模型的对应关系
"""
import abc
import functools
import uuid
from abc import abstractmethod
from logging import getLogger
from typing import Tuple, Union, Any

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import CollectionStatus, UpdateStatus

from kb.embedding.embedding_excep import EmbeddingNotFoundException
from kb.embedding.kb_embedding import get_embedding_model, EmbeddingModel
from kb.kb_config import QdrantConfig, DocxSchema
from kb.kb_excep import InvalidKBIdException

client = QdrantClient(location=QdrantConfig.LOCATION)

_logger = getLogger(__name__)


class Document:

    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata


class KnowledgeBase(abc.ABC):
    """知识库的抽象类"""

    @abstractmethod
    def remove_kb_split(self, ids: Union[str, list[str]]) -> bool:
        """
        从知识库中删除指定文档
        Args:
            ids: 文档id（可以一并删除多个）

        Returns:
            是否删除成功
        """

    @abstractmethod
    def add_kb_split(self, doc: Document):
        """
        添加知识片段（知识块）
        Args:
            doc: 知识块内容
        """
        pass

    @abstractmethod
    def query_doc(self, *args, query: str, filter_condition=None, limit=3, **kwargs) -> list[Document]:
        """
        查询知识库相关信息
        Args:
            query: 查询变量
            filter_condition: 查询过滤
            limit: 查询数量限制

        Returns:
            返回查询到的相关信息
        """
        pass

    @abstractmethod
    def filter_by(self, *arg, filter_condition: None, limit=3, offset=0, **kwargs):
        """
        知识库数据的条件过滤
        Args:
            filter_condition: 过滤文档片段的过滤条件
            limit: 条数限制
            offset: 偏移量

        Returns:
            返回符合条件的文档
        """
        pass


def parse_kb_id(kb_id: str) -> Tuple[str, str]:
    """
    从知识库id中解析相关信息

    Examples:
        标准格式为 `{kb_name};{embedding_model_id} `  ::

        - Hello;bge-m3
        - nihao;bge-m3
    Args:
        kb_id: 知识库id，和 `VectorKB.kb_id` 对应

    Returns:
        返回kb_id和embedding_model_id

    """
    kb_name, embedding_model_id = kb_id.split(";", 1)
    return kb_name, embedding_model_id


def ensure_kb_exist(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self._ensure_kb_with_size()
        return method(self, *args, **kwargs)

    return wrapper


class VectorKB(KnowledgeBase):
    """向量化的知识库"""

    def remove_kb_split(self, ids: Union[str, list[str]]) -> bool:
        ids = [ids] if isinstance(ids, str) else ids
        res = client.delete(
            collection_name=self.kb_id,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[VectorKB.build_filter(f'{DocxSchema.METADATA}.{DocxSchema.FILE_ID}', file_id)
                          for file_id in ids])
            )
        )
        return res.status == UpdateStatus.COMPLETED

    @ensure_kb_exist
    def filter_by(self, *arg, filter_condition: Union[dict[str, Any], models.Filter] = None, limit=3, offset=0,
                  **kwargs):
        query_filter = None
        if filter_condition:
            if len(filter_condition) == 0:
                return []
            else:
                query_filter = models.Filter(
                    must=[VectorKB.build_filter(f'{DocxSchema.METADATA}.{key}', match_value)
                          for key, match_value in filter_condition.items()])

        res = client.scroll(
            collection_name=self.kb_id,
            limit=limit,
            scroll_filter=query_filter,
            offset=offset,
            **kwargs
        )
        return [Document(point.payload[DocxSchema.PAGE_CONTENT], point.payload[DocxSchema.METADATA]) for
                point in res[0]]

    @ensure_kb_exist
    def add_kb_split(self, doc: Document):
        em = self.__get_embedding()(doc.page_content)
        res = client.upsert(
            collection_name=self.kb_id,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    payload=vars(doc),
                    vector=em.embedding
                )
            ]
        )
        return res

    @ensure_kb_exist
    def query_doc(self, *args, query: str, filter_condition: dict[str, Any] = None, limit=3, **kwargs) -> list[
        Document]:
        """
        查询过滤
        Args:
            query: 查询字符串
            filter_condition: 过滤条件，字典类型，前面为metadata中的字段，后面为匹配的值，默认为等价匹配，如果是列表则范围匹配，所有条件需要同时成立
            limit: 查询数据数量限制

        Returns:

        """
        query_filter = None
        if filter_condition:
            if len(filter_condition) == 0:
                return []
            else:
                query_filter = models.Filter(
                    must=[VectorKB.build_filter(f'{DocxSchema.METADATA}.{key}', match_value)
                          for key, match_value in filter_condition.items()])

        em = self.__get_embedding()(query)
        res = client.search(
            collection_name=self.kb_id,
            query_vector=em.embedding,
            limit=limit,
            query_filter=query_filter,
            **kwargs
        )
        return [Document(point.payload[DocxSchema.PAGE_CONTENT], point.payload[DocxSchema.METADATA]) for
                point in res]

    @staticmethod
    def build_filter(key, match_value):
        if isinstance(match_value, list):
            match = models.MatchAny(any=match_value)
        else:
            match = models.MatchValue(value=match_value)
        return models.FieldCondition(key=key, match=match)

    def __init__(self, kb_id: Union[str, Tuple[str, str]]):
        """
        创建知识库代理
        Args:
            kb_id: kb_id或者(kb_name, embedding_model_id)
        """
        if isinstance(kb_id, str):
            self.kb_id: str = kb_id
            """知识库id"""
            try:
                kb_name, embedding_model_id = parse_kb_id(kb_id)
            except ValueError as e:
                raise InvalidKBIdException(kb_id=kb_id)
        else:
            kb_name, embedding_model_id = kb_id
            self.kb_id: str = f"{kb_name};{embedding_model_id}"
        self.kb_name: str = kb_name
        """知识库名称"""
        self.embedding_model_id = embedding_model_id
        """Embedding模型的模型id，用id获取embedding模型对知识库Payload作向量化"""
        try:
            self.__get_embedding()
        except EmbeddingNotFoundException as e:
            _logger.warning(f"The EmbeddingModel-[{e.model_uid}] model used by KB-[{kb_name}] was not register. "
                            f"Please ensure is has been register before using KB-[{kb_name}]")

    def __get_embedding(self) -> EmbeddingModel:
        return get_embedding_model(model_uid=self.embedding_model_id)

    @property
    def size(self):
        return self.__get_embedding().size

    def _ensure_kb_with_size(self):
        """保证包含知识库的存在已经其大小相同，如果没有则创建，有则判断大小，如果大小不包含（多向量中没有），则抛出异常"""
        kb_id = self.kb_id
        size = self.size
        if not client.collection_exists(collection_name=kb_id):
            client.create_collection(
                collection_name=kb_id,
                vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE),
            )
            # 父亲节点id，加速父子查询
            client.create_payload_index(
                collection_name=kb_id,
                field_name=f"{DocxSchema.METADATA}.{DocxSchema.PARENT_ID}",
                field_schema="keyword"
            )
            # 文件id，加速文件过滤
            client.create_payload_index(
                collection_name=kb_id,
                field_name=f"{DocxSchema.METADATA}.{DocxSchema.FILE_ID}",
                field_schema="keyword"
            )
        # 无论创不创建都需要检查状态，因为我们保证创建之后没问题。
        collection_info = client.get_collection(kb_id)
        # 大小检查
        assert collection_info.config.params.vectors.size == size
        # 状态检查
        assert collection_info.status != CollectionStatus.RED

    def scroll(self, *args, **kwargs):
        return client.scroll(collection_name=self.kb_id, *args, **kwargs)


__kb_register: dict[str, KnowledgeBase] = {}


def get_kb_by_id(kb_id):
    if kb_id in __kb_register:
        return __kb_register[kb_id]
    else:
        __kb_register[kb_id] = VectorKB(kb_id)
    return __kb_register[kb_id]
