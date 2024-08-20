import os
from unittest import TestCase

from kb.kb_loader import DocxLoader


class TestDocxLoader(TestCase):
    test_file = "test.docx"

    def test_parse_to_tree(self):
        # 检测是否存在测试u文件
        file_path = TestDocxLoader.test_file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'【{file_path}】 测试文件文件不存在，请检查文件路径是否正确。')
        doc = DocxLoader(file_path)
        for e in doc:
            print(e.get_value_from_tree(), end='\n' + '-' * 100 + '\n\n')
        self.assertIsNotNone(doc)

    def test_lazy_load(self):
        file_path = TestDocxLoader.test_file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'【{file_path}】 测试文件文件不存在，请检查文件路径是否正确。')
        doc = DocxLoader(file_path)
        for d in doc.lazy_load():
            self.assertIsNotNone(d.page_content, d.metadata)
