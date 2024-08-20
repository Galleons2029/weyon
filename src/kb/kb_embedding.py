import abc
from abc import abstractmethod
from logging import getLogger
from typing import Callable, Any

from kb.embedding_excep import EmbeddingExistException, EmbeddingNotFoundException

logger = getLogger(__name__)


class EmbeddingModel(abc.ABC, Callable[[str], Any]):
    """文本向量化模型"""

    def __init__(self, size: int):
        self.size = size

    def __call__(self, query: str):
        return self.embed(query)

    @abstractmethod
    def embed(self, query: str):
        pass


__embeddings: dict[str, EmbeddingModel] = {}


def register(model_uid: str, model: EmbeddingModel):
    """
    将embedding模型注册到模型中
    :param model_uid: 模型id
    :param model: 模型
    :exception EmbeddingExistException 模型已经存在
    :return:
    """
    if model_uid in __embeddings:
        raise EmbeddingExistException(model_uid=model_uid)
    __embeddings[model_uid] = model


def get_embedding_model(model_uid: str) -> EmbeddingModel:
    if model_uid not in __embeddings:
        raise EmbeddingNotFoundException(model_uid=model_uid)
    return __embeddings[model_uid]


def get_all_embeddings():
    return __embeddings.copy()


class XinferenceEmbedding(EmbeddingModel):
    """XInference Embedding Model"""
    _TEST_TEXT: str = "Hello"

    def embed(self, query: str):
        res = self._client.embeddings.create(model=self.model_uid,
                                             input=[query])
        return res.data[-1]

    def __init__(self, client, model_uid: str):
        super().__init__(size=0)
        from openai import Client
        assert isinstance(client, Client)
        self._client = client
        self.model_uid = model_uid
        res = self(XinferenceEmbedding._TEST_TEXT)
        self.size = len(res.embedding)

    @staticmethod
    def from_api(api_key: str, base_url: str, model_uid: str):
        from openai import Client
        return XinferenceEmbedding(client=Client(api_key=api_key,
                                                 base_url=base_url),
                                   model_uid=model_uid)


from kb.kb_config import XinferenceConfig

register(XinferenceConfig.EMBEDDINGS, XinferenceEmbedding.from_api(api_key=XinferenceConfig.API_KEY,
                                                                   base_url=XinferenceConfig.BASE_URL,
                                                                   model_uid=XinferenceConfig.EMBEDDINGS))
