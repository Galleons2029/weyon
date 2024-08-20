import os
from unittest import TestCase

from fastapi.testclient import TestClient

from common import ResponseCode
from kb.kb_config import UploadConfig
from kb.kb_router import router, write_to_kb_with_docx

client = TestClient(router)


class Test(TestCase):
    test_file = 'test.docx'

    def test_upload_file(self):
        """测试文件上传的正常响应"""
        docx_file_path = Test.test_file
        with open(docx_file_path, 'rb') as docx_file:
            docx_content = docx_file.read()
        resp = client.put('/kb/Hello;bge-m3',
                           files={"file": ('example.docx', docx_content,
                                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('code'), ResponseCode.SUCCESS.value)
        file_path = os.path.join(UploadConfig.UPLOAD_SAVING_PATH, resp.json().get('data') + '.docx')
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def tearDown(self):
        if os.path.exists(UploadConfig.UPLOAD_SAVING_PATH):
            os.rmdir(UploadConfig.UPLOAD_SAVING_PATH)

    def test_write_to_kb_with_docx(self):
        docx_file_path = Test.test_file
        kb_id = write_to_kb_with_docx(docx_file_path, "Hello;bge-m3", filename="test.docx")
        self.assertEqual("Hello;bge-m3", kb_id)

    def test_query_kb(self):
        resp = client.get("/kb/Hello;bge-m3",
                          params={
                              "query": "Hello"
                          }
                          )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('code'), ResponseCode.SUCCESS.value)
        self.assertGreaterEqual(len(resp.json().get('data')), 1)
