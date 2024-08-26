import os
from unittest import TestCase

from fastapi.testclient import TestClient

from common import ResponseCode
from kb.kb_config import UploadConfig
from kb.kb_router import router

client = TestClient(router)


class Test(TestCase):
    test_file = 'test.docx'

    def test_upload_file(self):
        """测试文件上传的正常响应"""
        docx_file_path = Test.test_file
        with open(docx_file_path, 'rb') as docx_file:
            docx_content = docx_file.read()
        resp = client.put('/kb/file/Hello;bge-m3',
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

    def test_query_kb(self):
        resp = client.get("/kb/Hello;bge-m3",
                          params={
                              "query": "Hello"
                          })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('code'), ResponseCode.SUCCESS.value)
        self.assertGreaterEqual(len(resp.json().get('data')), 1)

    def test_filter_kb(self):
        resp = client.post('/kb/Hello;bge-m3')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('code'), ResponseCode.SUCCESS.value)
        self.assertGreaterEqual(len(resp.json().get('data')), 1)

    def test_delete_doc(self):
        resp = client.delete('/kb/Hello;bge-m3',
                             params={
                                 "doc_ids": "dsfasdfadsfa"
                             })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('code'), ResponseCode.SUCCESS.value)
        self.assertEqual(resp.json().get('msg'), "成功删除")
