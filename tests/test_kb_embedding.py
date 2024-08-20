from unittest import TestCase

from openai import Client

from kb.embedding.embedding_excep import EmbeddingExistException
from kb.embedding.kb_embedding import XinferenceEmbedding, get_embedding_model, register
from kb.kb_config import XinferenceConfig


class TestXinferenceEmbedding(TestCase):
    def test_embed(self):
        client = Client(api_key=XinferenceConfig.API_KEY, base_url=XinferenceConfig.BASE_URL)
        em = XinferenceEmbedding(client=client, model_uid=XinferenceConfig.EMBEDDINGS)
        res = em("hello")
        self.assertIsNotNone(res)

    def test_from_api(self):
        em = XinferenceEmbedding.from_api(api_key=XinferenceConfig.API_KEY,
                                          base_url=XinferenceConfig.BASE_URL,
                                          model_uid=XinferenceConfig.EMBEDDINGS)
        res = em("hello")
        self.assertIsNotNone(res)

    def test_get_embedding_model(self):
        em = get_embedding_model(XinferenceConfig.EMBEDDINGS)
        res = em("hello")
        self.assertIsNotNone(res)

    def test_register_with_twice(self):
        em = XinferenceEmbedding.from_api(api_key=XinferenceConfig.API_KEY,
                                          base_url=XinferenceConfig.BASE_URL,
                                          model_uid=XinferenceConfig.EMBEDDINGS)
        with self.assertRaises(EmbeddingExistException) as cm:
            register(model_uid=XinferenceConfig.EMBEDDINGS, model=em)
        self.assertEquals(cm.exception.model_uid, XinferenceConfig.EMBEDDINGS)
