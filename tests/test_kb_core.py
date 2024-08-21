from unittest import TestCase

import qdrant_client.models

from kb.kb_core import VectorKB, Document


class TestVectorKB(TestCase):
    test_kb_id = "Hello;bge-m3"

    def test_add_kb_split(self):
        test_kb = VectorKB(kb_id=TestVectorKB.test_kb_id)
        res = test_kb.add_kb_split(Document("Hello", metadata={"_id": "wuhu"}))
        self.assertIsInstance(res, qdrant_client.models.UpdateResult)

    def test_query_doc(self):
        test_kb = VectorKB(kb_id=TestVectorKB.test_kb_id)
        docs = test_kb.query_doc("Hello")
        self.assertGreaterEqual(len(docs), 1)

    def test_filter_by(self):
        test_kb = VectorKB(kb_id=TestVectorKB.test_kb_id)
        res = test_kb.filter_by()
        self.assertGreaterEqual(len(res), 1)

    def test_size(self):
        test_kb = VectorKB(kb_id=TestVectorKB.test_kb_id)
        self.assertEqual(1024, test_kb.size)
