import unittest
from unittest.mock import MagicMock
from bcrypt import hashpw, gensalt

from src.db import get_db
from src.auth.service import Authentication as auth_service


class TestAuthentication(unittest.TestCase):
    hashed_password = hashpw("password".encode(),
                             gensalt()).decode()

    def test_verify_password_pass(self):
        self.assertIs(True,
                      auth_service.verify_password(
                          auth_service,
                          plain_password="password",
                          hashed_password=self.hashed_password
                      ))

    def test_verify_password_failed(self):
        self.assertIs(False,
                      auth_service.verify_password(
                          auth_service,
                          plain_password="secret",
                          hashed_password=self.hashed_password
                      ))


if __name__ == "__main__":
    unittest.main()
