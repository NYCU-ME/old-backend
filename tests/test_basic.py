import unittest
from flask import url_for
from main import app

class BasicTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        if self.app_context:
            self.app_context.pop()

    def test_app_is_alive(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 404)

    def test_app_sync_repo_endpoint(self):
        res = self.client.get("/sync_repo")
        self.assertEqual(res.status_code, 405)
