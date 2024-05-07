import unittest
from datetime import datetime, timedelta, timezone

from bcrypt import hashpw, gensalt
from jose import jwt

from src.db import get_db
from src.auth.service import Authentication as auth_service


class TestAuthentication(unittest.TestCase):
    hashed_password = hashpw("password".encode(),
                             gensalt()).decode()

    def test_verify_password_success(self):
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

    def test_create_refresh_token_success(self):
        current_time = datetime.now(timezone.utc)
        expiration = current_time + timedelta(days=7)
        token = auth_service.create_refresh_token(
            auth_service,
            email="some@email.com",
        )
        check_payload = {'sub': 'some@email.com',
                         'exp': int(expiration.timestamp()),
                         'scope': 'refresh_token'}
        payload = jwt.decode(token=token,
                             key=auth_service.SECRET_512,
                             algorithms=[auth_service.REFRESH_ALGORITHM],
                             )
        self.assertDictEqual(payload, check_payload)


if __name__ == "__main__":
    unittest.main()
