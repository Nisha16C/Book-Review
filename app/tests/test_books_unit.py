import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

def test_get_books_endpoint_with_cache_hit(client: TestClient):
    """Unit test: GET /books endpoint with cache hit"""
    cached_books = [
        {
            "id": 1,
            "title": "Cached Book",
            "author": "Author 1",
            "isbn": "1234567890123",
            "description": "Test description",
            "published_year": 2023,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": None
        }
    ]
    
    with patch('app.api.books.cache_service.get', return_value=cached_books):
        response = client.get("/api/v1/books/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Cached Book"

def test_get_books_endpoint_with_cache_miss(client: TestClient, sample_book_data):
    """Unit test: GET /books endpoint with cache miss"""
    # Create mock database session and query results
    mock_book = MagicMock()
    mock_book.id = 1
    mock_book.title = sample_book_data["title"]
    mock_book.author = sample_book_data["author"]
    mock_book.isbn = sample_book_data.get("isbn")
    mock_book.description = sample_book_data.get("description")
    mock_book.published_year = sample_book_data.get("published_year")
    mock_book.created_at = datetime.now()
    mock_book.updated_at = None
    
    mock_query = MagicMock()
    mock_query.offset.return_value.limit.return_value.all.return_value = [mock_book]
    
    mock_session = MagicMock()
    mock_session.query.return_value = mock_query
    
    with patch('app.api.books.cache_service.get', return_value=None) as mock_cache_get, \
         patch('app.api.books.cache_service.set', return_value=True) as mock_cache_set, \
         patch('app.db.database.get_db', return_value=iter([mock_session])), \
         patch('app.services.book_service.BookService.get_books', return_value=[mock_book]):
        
        response = client.get("/api/v1/books/")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

def test_get_books_endpoint_with_cache_error(client: TestClient, sample_book_data):
    """Unit test: GET /books endpoint handles cache errors gracefully"""
    # Create mock database session and query results
    mock_book = MagicMock()
    mock_book.id = 1
    mock_book.title = sample_book_data["title"]
    mock_book.author = sample_book_data["author"]
    mock_book.isbn = sample_book_data.get("isbn")
    mock_book.description = sample_book_data.get("description")
    mock_book.published_year = sample_book_data.get("published_year")
    mock_book.created_at = datetime.now()
    mock_book.updated_at = None
    
    mock_session = MagicMock()
    
    # Mock cache service to raise exception
    with patch('app.api.books.cache_service.get', side_effect=Exception("Cache error")), \
         patch('app.db.database.get_db', return_value=iter([mock_session])), \
         patch('app.services.book_service.BookService.get_books', return_value=[mock_book]):
        
        response = client.get("/api/v1/books/")
        
        # Should still work, falling back to database
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

def test_get_books_endpoint_pagination(client: TestClient):
    """Unit test: GET /books endpoint with pagination"""
    cached_data = [
        {
            "id": 1,
            "title": "Test Book",
            "author": "Test Author",
            "isbn": None,
            "description": None,
            "published_year": None,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": None
        }
    ]
    
    with patch('app.api.books.cache_service.get', return_value=cached_data):
        response = client.get("/api/v1/books/?skip=10&limit=50")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

def test_create_book_endpoint_success(client: TestClient, sample_book_data):
    """Unit test: POST /books endpoint successful creation"""
    # Create mock book instance
    mock_book = MagicMock()
    mock_book.id = 1
    mock_book.title = sample_book_data["title"]
    mock_book.author = sample_book_data["author"]
    mock_book.isbn = sample_book_data.get("isbn")
    mock_book.description = sample_book_data.get("description")
    mock_book.published_year = sample_book_data.get("published_year")
    mock_book.created_at = datetime.now()
    mock_book.updated_at = None
    
    mock_session = MagicMock()
    
    with patch('app.api.books.cache_service.delete', return_value=True), \
         patch('app.db.database.get_db', return_value=iter([mock_session])), \
         patch('app.services.book_service.BookService.create_book', return_value=mock_book):
        
        response = client.post("/api/v1/books/", json=sample_book_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_book_data["title"]
        assert data["author"] == sample_book_data["author"]

def test_create_book_endpoint_with_cache_invalidation_failure(client: TestClient, sample_book_data):
    """Unit test: POST /books endpoint handles cache invalidation failure"""
    # Create mock book instance
    mock_book = MagicMock()
    mock_book.id = 1
    mock_book.title = sample_book_data["title"]
    mock_book.author = sample_book_data["author"]
    mock_book.isbn = sample_book_data.get("isbn")
    mock_book.description = sample_book_data.get("description")
    mock_book.published_year = sample_book_data.get("published_year")
    mock_book.created_at = datetime.now()
    mock_book.updated_at = None
    
    mock_session = MagicMock()
    
    with patch('app.api.books.cache_service.delete', side_effect=Exception("Cache error")), \
         patch('app.db.database.get_db', return_value=iter([mock_session])), \
         patch('app.services.book_service.BookService.create_book', return_value=mock_book):
        
        response = client.post("/api/v1/books/", json=sample_book_data)
        
        # Should still succeed
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_book_data["title"]

def test_create_book_endpoint_validation(client: TestClient):
    """Unit test: POST /books endpoint input validation"""
    invalid_book_data = {
        "description": "Book without title and author"
    }
    
    response = client.post("/api/v1/books/", json=invalid_book_data)
    assert response.status_code == 422

def test_create_book_endpoint_minimal_data(client: TestClient):
    """Unit test: POST /books endpoint with minimal required data"""
    minimal_book_data = {
        "title": "Minimal Book",
        "author": "Minimal Author"
    }
    
    # Create mock book instance
    mock_book = MagicMock()
    mock_book.id = 1
    mock_book.title = minimal_book_data["title"]
    mock_book.author = minimal_book_data["author"]
    mock_book.isbn = None
    mock_book.description = None
    mock_book.published_year = None
    mock_book.created_at = datetime.now()
    mock_book.updated_at = None
    
    mock_session = MagicMock()
    
    with patch('app.api.books.cache_service.delete', return_value=True), \
         patch('app.db.database.get_db', return_value=iter([mock_session])), \
         patch('app.services.book_service.BookService.create_book', return_value=mock_book):
        
        response = client.post("/api/v1/books/", json=minimal_book_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == minimal_book_data["title"]
        assert data["author"] == minimal_book_data["author"]