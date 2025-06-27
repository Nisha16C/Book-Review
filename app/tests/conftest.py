import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the Backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.main import app
from app.db.database import get_db, Base

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def sample_book_data():
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890123",
        "description": "A test book description",
        "published_year": 2023
    }

@pytest.fixture
def sample_review_data():
    return {
        "reviewer_name": "Test Reviewer",
        "rating": 5,
        "comment": "Great book!"
    }