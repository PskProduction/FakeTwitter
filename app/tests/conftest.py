import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import User
from main import app
from db.database import Base
from db.database import get_db

DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def test_engine():
    engine = create_engine(DATABASE_URL)
    return engine


@pytest.fixture
def test_db(test_engine):
    session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    Base.metadata.create_all(bind=test_engine)

    db = session()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_users(test_db):
    test_users_data = [
        {"username": "user1", "api_key": "test"},
        {"username": "user2", "api_key": "test2"},
    ]

    test_users = []
    for user_data in test_users_data:
        existing_user = test_db.query(User).filter_by(username=user_data["username"]).first()

        if not existing_user:
            user = User(**user_data)
            test_db.add(user)
            test_db.commit()
            test_db.refresh(user)
            test_users.append(user)
        else:
            test_users.append(existing_user)

    return test_users


@pytest.fixture
def test_app(test_db):
    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app, base_url='http://127.0.0.1:8000')
    return client
