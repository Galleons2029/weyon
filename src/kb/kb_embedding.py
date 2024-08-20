import abc
from abc import abstractmethod
from logging import getLogger
from typing import Callable, Any

logger = getLogger(__name__)

__embeddings = {}


class EmbeddingModel(abc.ABC, Callable[[str], Any]):
    """文本向量化模型"""

    def __call__(self, query: str):
        return self.embed(query)

    @abstractmethod
    def embed(self, query: str):
        pass


def register(model_id: str, model: Callable[[str], Any], overwrite=False):
    """
    将embedding模型注册到模型中
    :param model_id:
    :param model:
    :param overwrite:
    :return:
    """
    if model_id in __embeddings and not overwrite:
        raise KeyError(
            f"There has been a Embedding Model named {model_id},if you want overwrite you can use `overwrite=True`")
    logger.info(f"Register EmbeddingModel-[{model_id}]")
    __embeddings[model_id] = model


class XinferenceEmbedding(EmbeddingModel):
    """XInference Embedding Model"""
    _TEST_TEXT: str = "Hello"

    def embed(self, query: str):
        res = self._client.embeddings.create(model=self.model_uid,
                                             input=[query])
        return res.data[-1]

    def __init__(self, client, model_uid: str):
        super().__init__()
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
