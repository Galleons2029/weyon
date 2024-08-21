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
from qdrant_client.http.models import CollectionStatus

from kb.embedding.embedding_excep import EmbeddingNotFoundException
from kb.embedding.kb_embedding import get_embedding_model, EmbeddingModel
from kb.kb_config import QdrantConfig

client = QdrantClient(location=QdrantConfig.LOCATION)

logger = getLogger(__name__)


class Document:

    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata


class KnowledgeBase(abc.ABC):
    """知识库的抽象类"""

    @abstractmethod
    def add_kb_split(self, doc: Document):
        """
        添加知识片段（知识块）
        :param doc: 知识块内容
        :return:
        """
        pass

    @abstractmethod
    def query_doc(self, query: str, filter_condition=None, limit=3, *args, **kwargs) -> list[Document]:
        """
        查询知识库相关信息
        :param query: 查询变量
        :param filter_condition: 查询过滤
        :param limit: 查询数量限制
        :return: 返回查询到的相关信息
        """
        pass

    @abstractmethod
    def filter_by(self, filter_condition: None, limit=3, offset=0, *arg, **kwargs):
        """
        知识库数据的条件过滤
        :param filter_condition: 过滤文档片段的过滤条件
        :param limit: 条数限制
        :param offset: 偏移量
        :return: 返回符合条件的文档
        """
        pass


def parse_kb_id(kb_id: str) -> Tuple[str, str]:
    """
    从知识库id中解析相关信息，标准格式为:
            {kb_id};{embedding_model_id}
    :param kb_id: 知识库id，和 `VectorKB.kb_id` 对应
    :return: 返回kb_id和embedding_model_id
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

    @ensure_kb_exist
    def filter_by(self, filter_condition: Union[dict[str, Any], models.Filter] = None, limit=3, offset=0, *arg,
                  **kwargs):
        query_filter = None
        if filter_condition:
            if len(filter_condition) == 0:
                return []
            else:
                query_filter = models.Filter(
                    must=[VectorKB.build_filter(f'metadata.{key}', match_value)
                          for key, match_value in filter_condition.items()])

        res = client.scroll(
            collection_name=self.kb_id,
            limit=limit,
            scroll_filter=query_filter,
            offset=offset,
            **kwargs
        )
        return [Document(point.payload['page_content'], point.payload['metadata']) for point in res[0]]

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
    def query_doc(self, query: str, filter_condition: dict[str, Any] = None, limit=3, *args, **kwargs) -> list[
        Document]:
        """
        查询过滤
        :param query: 查询字符串
        :param filter_condition: 过滤条件，字典类型，前面为metadata中的字段，后面为匹配的值，默认为等价匹配，如果是列表则范围匹配，所有条件需要同时成立
        :param limit: 查询数据数量限制
        :param args:
        :param kwargs:
        :return:
        """
        query_filter = None
        if filter_condition:
            if len(filter_condition) == 0:
                return []
            else:
                query_filter = models.Filter(
                    must=[VectorKB.build_filter(f'metadata.{key}', match_value)
                          for key, match_value in filter_condition.items()])

        em = self.__get_embedding()(query)
        res = client.search(
            collection_name=self.kb_id,
            query_vector=em.embedding,
            limit=limit,
            query_filter=query_filter,
            **kwargs
        )
        return [Document(point.payload['page_content'], point.payload['metadata']) for point in res]

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
        :param kb_id: kb_id或者(kb_name, embedding_model_id)
        """
        if isinstance(kb_id, str):
            self.kb_id: str = kb_id
            """知识库id"""
            kb_name, embedding_model_id = parse_kb_id(kb_id)
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
            logger.warning(f"The EmbeddingModel-[{e.model_uid}] model used by KB-[{kb_name}] was not register. "
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
