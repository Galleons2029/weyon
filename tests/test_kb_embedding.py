from unittest import TestCase

from openai import Client

from kb.kb_config import XinferenceConfig
from kb.kb_embedding import XinferenceEmbedding


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
