"""
知识库注册中心，负责管理知识库的注册和知识库和向量模型的对应关系
"""
import abc
import functools
import uuid
from abc import abstractmethod
from logging import getLogger
from typing import Tuple, Union

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
    def query_doc(self, query: str, config=None) -> list[Document]:
        """
        查询知识库相关信息
        :param query: 查询变量
        :param config: 查询配置
        :return: 返回查询到的相关信息
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
    def query_doc(self, query: str, config=None) -> list[Document]:
        if config is None:
            config = {}
        em = self.__get_embedding()(query)
        res = client.search(
            collection_name=self.kb_id,
            query_vector=em.embedding,
            **config
        )
        return [Document(point.payload['page_content'], point.payload['metadata']) for point in res]

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
