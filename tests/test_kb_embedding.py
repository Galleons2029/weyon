from unittest import TestCase

from openai import Client

from kb.embedding.embedding_excep import EmbeddingExistException
from kb.embedding.kb_embedding import OpenAIEmbedding, get_embedding_model, register
from kb.kb_config import EmbeddingConfig


class TestXinferenceEmbedding(TestCase):
    def test_embed(self):
        client = Client(api_key=EmbeddingConfig.API_KEY, base_url=EmbeddingConfig.BASE_URL)
        em = OpenAIEmbedding(client=client, model_uid=EmbeddingConfig.EMBEDDINGS)
        res = em("hello")
        self.assertIsNotNone(res)

    def test_from_api(self):
        em = OpenAIEmbedding.from_api(api_key=EmbeddingConfig.API_KEY,
                                      base_url=EmbeddingConfig.BASE_URL,
                                      model_uid=EmbeddingConfig.EMBEDDINGS)
        res = em("hello")
        self.assertIsNotNone(res)

    def test_get_embedding_model(self):
        em = get_embedding_model(EmbeddingConfig.EMBEDDINGS)
        res = em("hello")
        self.assertIsNotNone(res)

    def test_register_with_twice(self):
        em = OpenAIEmbedding.from_api(api_key=EmbeddingConfig.API_KEY,
                                      base_url=EmbeddingConfig.BASE_URL,
                                      model_uid=EmbeddingConfig.EMBEDDINGS)
        with self.assertRaises(EmbeddingExistException) as cm:
            register(model_uid=EmbeddingConfig.EMBEDDINGS, model=em)
        self.assertEqual(cm.exception.model_uid, EmbeddingConfig.EMBEDDINGS)
