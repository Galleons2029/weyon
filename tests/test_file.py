import os
from unittest import TestCase

from fastapi.testclient import TestClient

from common import ResponseCode
from kb.kb_config import UploadConfig
from kb.kb_router import router

client = TestClient(router)


class Test(TestCase):
    def test_upload_file(self):
        """测试文件上传的正常响应"""
        docx_file_path = 'test.docx'
        with open(docx_file_path, 'rb') as docx_file:
            docx_content = docx_file.read()
        resp = client.post('/kb/upload/',
                           files={"file": ('example.docx', docx_content,
                                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('code'), ResponseCode.SUCCESS.value)
        file_path = os.path.join(UploadConfig.UPLOAD_SAVING_PATH, resp.json().get('data') + '.docx')
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def tearDown(self):
        os.rmdir(UploadConfig.UPLOAD_SAVING_PATH)
