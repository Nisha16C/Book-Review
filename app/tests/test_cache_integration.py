import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_cache.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(setup_database):
    """Test client fixture"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def sample_book_data():
    """Sample book data fixture"""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890123",
        "description": "Test Description",
        "published_year": 2023
    }

def test_cache_miss_integration_flow(client: TestClient, sample_book_data):
    """Integration test: Complete cache-miss flow from API to database"""
    
    # Mock cache service for book creation
    with patch('app.api.books.cache_service.delete', return_value=True):
        create_response = client.post("/api/v1/books/", json=sample_book_data)
        assert create_response.status_code == 201
        created_book = create_response.json()
    
    # Mock cache service to simulate cache miss for get operation
    with patch('app.api.books.cache_service.get', return_value=None) as mock_cache_get, \
         patch('app.api.books.cache_service.set', return_value=True) as mock_cache_set:
        
        response = client.get("/api/v1/books/")
        
        # Verify database was queried after cache miss
        assert response.status_code == 200
        books_data = response.json()
        assert len(books_data) >= 1
        
        # Verify returned data matches database
        returned_book = next((book for book in books_data if book["id"] == created_book["id"]), None)
        assert returned_book is not None
        assert returned_book["id"] == created_book["id"]
        assert returned_book["title"] == sample_book_data["title"]

def test_cache_miss_with_multiple_books(client: TestClient):
    """Integration test: Cache miss with multiple books in database"""
    
    books_data = [
        {"title": "Cache Book 1", "author": "Author 1", "isbn": "1111111111111", "description": "Description 1"},
        {"title": "Cache Book 2", "author": "Author 2", "isbn": "2222222222222", "description": "Description 2"},
        {"title": "Cache Book 3", "author": "Author 3", "isbn": "3333333333333", "description": "Description 3"}
    ]
    
    created_books = []
    # Create multiple books
    with patch('app.api.books.cache_service.delete', return_value=True):
        for book_data in books_data:
            response = client.post("/api/v1/books/", json=book_data)
            assert response.status_code == 201
            created_books.append(response.json())
    
    # Test cache miss scenario
    with patch('app.api.books.cache_service.get', return_value=None), \
         patch('app.api.books.cache_service.set', return_value=True):
        
        response = client.get("/api/v1/books/")
        
        assert response.status_code == 200
        returned_books = response.json()
        assert len(returned_books) >= 3
        
        # Verify our created books are in the response
        created_titles = {book["title"] for book in created_books}
        returned_titles = {book["title"] for book in returned_books}
        assert created_titles.issubset(returned_titles)

def test_cache_miss_with_pagination_integration(client: TestClient):
    """Integration test: Cache miss with pagination parameters"""
    
    # Create multiple books
    created_books = []
    with patch('app.api.books.cache_service.delete', return_value=True):
        for i in range(5):
            book_data = {
                "title": f"Pagination Book {i+1}", 
                "author": f"Pagination Author {i+1}",
                "isbn": f"123456789012{i}",
                "description": f"Pagination Description {i+1}"
            }
            response = client.post("/api/v1/books/", json=book_data)
            assert response.status_code == 201
            created_books.append(response.json())
    
    # Test cache miss with pagination
    with patch('app.api.books.cache_service.get', return_value=None), \
         patch('app.api.books.cache_service.set', return_value=True):
        
        response = client.get("/api/v1/books/?skip=1&limit=3")
        
        assert response.status_code == 200
        books = response.json()
        assert len(books) <= 3
        assert isinstance(books, list)

def test_cache_miss_error_recovery_integration(client: TestClient, sample_book_data):
    """Integration test: Error recovery during cache miss flow"""
    
    # Create test data
    with patch('app.api.books.cache_service.delete', return_value=True):
        create_response = client.post("/api/v1/books/", json=sample_book_data)
        assert create_response.status_code == 201
        created_book = create_response.json()
    
    # Simulate cache miss but set failure
    with patch('app.api.books.cache_service.get', return_value=None), \
         patch('app.api.books.cache_service.set', return_value=False):
        
        response = client.get("/api/v1/books/")
        
        # Should still return data from database
        assert response.status_code == 200
        books = response.json()
        assert len(books) >= 1
        
        # Verify our created book is in the response
        returned_book = next((book for book in books if book["id"] == created_book["id"]), None)
        assert returned_book is not None
        assert returned_book["title"] == sample_book_data["title"]

def test_cache_miss_edge_cases_integration(client: TestClient):
    """Integration test: Edge cases during cache miss"""
    
    # Test cache miss - may have existing data in database
    with patch('app.api.books.cache_service.get', return_value=None), \
         patch('app.api.books.cache_service.set', return_value=True):
        
        response = client.get("/api/v1/books/")
        
        # Should return successful response (may be empty or have existing data)
        assert response.status_code == 200
        books = response.json()
        assert isinstance(books, list)

def test_cache_hit_scenario(client: TestClient):
    """Integration test: Cache hit scenario"""
    
    # Mock cached data
    cached_books = [
        {
            "id": 1,
            "title": "Cached Book",
            "author": "Cached Author",
            "isbn": "9999999999999",
            "description": "Cached Description",
            "published_year": 2023,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    ]
    
    # Mock cache hit
    with patch('app.api.books.cache_service.get', return_value=cached_books), \
         patch('app.api.books.cache_service.set') as mock_cache_set:
        
        response = client.get("/api/v1/books/")
        
        assert response.status_code == 200
        books = response.json()
        assert len(books) == 1
        assert books[0]["title"] == "Cached Book"
        
        # Verify cache set was not called (cache hit)
        mock_cache_set.assert_not_called()

def test_cache_service_exception_handling(client: TestClient, sample_book_data):
    """Integration test: Cache service exception handling"""
    
    # Create test data first
    with patch('app.api.books.cache_service.delete', return_value=True):
        create_response = client.post("/api/v1/books/", json=sample_book_data)
        assert create_response.status_code == 201
        created_book = create_response.json()
    
    # Simulate cache service throwing exception
    with patch('app.api.books.cache_service.get', side_effect=Exception("Cache service down")):
        
        response = client.get("/api/v1/books/")
        
        # Should still return data from database despite cache error
        assert response.status_code == 200
        books = response.json()
        assert len(books) >= 1
        
        # Verify our created book is in the response
        returned_book = next((book for book in books if book["id"] == created_book["id"]), None)
        assert returned_book is not None
        assert returned_book["title"] == sample_book_data["title"]

def test_cache_invalidation_on_book_creation(client: TestClient, sample_book_data):
    """Integration test: Cache invalidation after book creation"""
    
    # Mock cache operations
    with patch('app.api.books.cache_service.delete', return_value=True) as mock_cache_delete:
        
        response = client.post("/api/v1/books/", json=sample_book_data)
        
        assert response.status_code == 201
        created_book = response.json()
        assert created_book["title"] == sample_book_data["title"]
        
        # Verify cache invalidation was called
        assert mock_cache_delete.call_count >= 1

def test_cache_invalidation_failure_handling(client: TestClient, sample_book_data):
    """Integration test: Handle cache invalidation failures gracefully"""
    
    # Mock cache delete to fail but don't raise exception in the endpoint
    with patch('app.api.books.cache_service.delete', return_value=False):
        
        response = client.post("/api/v1/books/", json=sample_book_data)
        
        # Should still create book successfully despite cache invalidation failure
        assert response.status_code == 201
        created_book = response.json()
        assert created_book["title"] == sample_book_data["title"]