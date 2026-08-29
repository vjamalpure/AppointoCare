import os
import unittest

os.environ["DATABASE_URL"] = "sqlite:///app-test.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"

from app import create_app, db


class AppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)

    def setUp(self):
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
        try:
            os.remove("app-test.db")
        except FileNotFoundError:
            pass

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_readiness_endpoint(self):
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["database"], "available")

    def test_services_require_authentication(self):
        response = self.client.get("/service/all")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
