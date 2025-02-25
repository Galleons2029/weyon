import abc
from abc import abstractmethod
from logging import getLogger
from typing import Callable, Any

from openai.types.embedding import Embedding

from kb.embedding.embedding_excep import EmbeddingExistException, EmbeddingNotFoundException

_logger = getLogger(__name__)


class EmbeddingModel(abc.ABC, Callable[[str], Any]):
    """文本向量化模型"""

    def __init__(self, size: int):
        self.size = size

    def __call__(self, query: str) -> Embedding:
        return self.embed(query)

    @abstractmethod
    def embed(self, query: str) -> Embedding:
        pass


__embeddings: dict[str, EmbeddingModel] = {}


def register(model_uid: str, model: EmbeddingModel):
    """
    将embedding模型注册到模型中
    Args:
        model_uid: 模型id
        model: 模型

    Raises:
        EmbeddingExistException: 模型已经存在
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


class OpenAIEmbedding(EmbeddingModel):
    """OpenAI Embedding Model"""
    _TEST_TEXT: str = "Hello"

    def embed(self, query: str) -> Embedding:
        res = self._client.embeddings.create(model=self.model_uid,
                                             input=[query])
        return res.data[-1]

    def __init__(self, client, model_uid: str):
        super().__init__(size=0)
        from openai import Client
        assert isinstance(client, Client)
        self._client = client
        self.model_uid = model_uid
        res = self(OpenAIEmbedding._TEST_TEXT)
        self.size = len(res.embedding)

    @staticmethod
    def from_api(api_key: str, base_url: str, model_uid: str):
        from openai import Client
        return OpenAIEmbedding(client=Client(api_key=api_key,
                                             base_url=base_url),
                               model_uid=model_uid)


from kb.kb_config import EmbeddingConfig

embeds = [EmbeddingConfig.EMBEDDINGS] if isinstance(EmbeddingConfig.EMBEDDINGS, str) else EmbeddingConfig.EMBEDDINGS

for emb in embeds:
    register(emb, OpenAIEmbedding.from_api(api_key=EmbeddingConfig.API_KEY,
                                           base_url=EmbeddingConfig.BASE_URL,
                                           model_uid=emb))
