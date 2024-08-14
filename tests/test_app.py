from unittest import TestCase

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class Test(TestCase):
    def test_root(self):
        resp = client.get('/')
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json(), {"message": "Hello World"})
