from unittest import TestCase

from kb.doc_retriever import get_doc_kb_by_id


class Test(TestCase):
    def test_get_doc_kb_by_id(self):
        kb = get_doc_kb_by_id('Hello;bge-m3')
        res = kb.query_doc(query="长沙理工大学23年就业数据")
        self.assertGreaterEqual(len(res), 1)
