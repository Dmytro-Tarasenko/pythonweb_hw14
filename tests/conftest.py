from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.main import app
import src.db as database
from src.auth.service import Authentication as auth_service


# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.sqlite"

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False},
                       poolclass=StaticPool)

TestSession = sessionmaker(autocommit=False,
                           autoflush=False,
                           bind=engine)


@pytest.fixture(scope='session')
def session():
    database.Base.metadata.drop_all(bind=engine)
    database.Base.metadata.create_all(bind=engine)
    print(database.Base.metadata.tables)
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope='module')
def client(session):
    # Dependency override
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[RateLimiter] = AsyncMock()

    yield TestClient(app)


@pytest.fixture(scope='module')
def user():
    return {
        "fullname": "Luk Skywoker",
        "email": "djedai@tatuin.emp",
        "hashed_pwd": "May_the_4th",
        "id": 1,
        "loggedin": True,
        "email_confirmed": True,
        "avatar_url": "cloudinary_url"
    }


@pytest.fixture(scope='module')
def get_access_token():
    return auth_service.create_access_token(
        auth_service,
        email="djedai@tatuin.emp"
    )