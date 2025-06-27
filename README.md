# Book Review Service

A comprehensive RESTful API service for managing books and their reviews, built with FastAPI, PostgreSQL, and Redis caching.

## 🚀 Features

- **RESTful API** with OpenAPI/Swagger documentation
- **PostgreSQL** database with SQLAlchemy ORM
- **Redis caching** for improved performance
- **Database migrations** with Alembic
- **Comprehensive testing** with pytest
- **Docker support** for easy deployment
- **Proper error handling** and logging
- **Input validation** with Pydantic

## 📋 API Endpoints

- `GET /api/v1/books` - List all books (with caching)
- `POST /api/v1/books` - Create a new book
- `GET /api/v1/books/{id}/reviews` - Get reviews for a specific book
- `POST /api/v1/books/{id}/reviews` - Create a review for a book

## 🛠️ Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+ (optional, for caching)
- Docker & Docker Compose (optional)

### 🐳 Option 1: Docker Compose (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/Nisha16CGit/Book-Review.git
cd Book-Review
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Run database migrations:**
```bash
docker-compose exec app alembic upgrade head
```

4. **Seed the database (optional):**
```bash
docker-compose exec app python scripts/seed_data.py
```

5. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### 💻 Option 2: Local Development

1. **Clone and setup:**
```bash
git clone https://github.com/Nisha16CGit/Book-Review.git
cd Book-Review
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup PostgreSQL database:**
```bash
createdb book_review
```

3. **Setup environment variables:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run migrations:**
```bash
alembic upgrade head
```

5. **Start the application:**
```bash
uvicorn app.main:app --reload
```

## 🗄️ Database Management

### Running Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migrations:
```bash
alembic downgrade -1
```

### Initialize Database

```bash
python scripts/init_db.py
```

### Seed Sample Data

```bash
python scripts/seed_data.py
```

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test files:
```bash
pytest app/tests/test_books_unit.py -v
pytest app/tests/test_cache_integration.py -v
```

### Test Categories

- **Unit Tests**: Test individual endpoints and functions (`test_books_unit.py`)
- **Integration Tests**: Test cache integration and database interactions (`test_cache_integration.py`)
- **Error Handling Tests**: Test graceful error handling when services are down

## 📚 API Documentation

Once the service is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Usage

#### Create a Book
```bash
curl -X POST "http://localhost:8000/api/v1/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "9780743273565",
    "description": "A classic American novel",
    "published_year": 1925
  }'
```

#### Get All Books
```bash
curl "http://localhost:8000/api/v1/books/"
```

#### Create a Review
```bash
curl -X POST "http://localhost:8000/api/v1/books/1/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "reviewer_name": "John Doe",
    "rating": 5,
    "comment": "Excellent book!"
  }'
```

#### Get Book Reviews
```bash
curl "http://localhost:8000/api/v1/books/1/reviews"
```

## 🏗️ Architecture

### Project Structure
```
Book-Review/
├── app/
│   ├── api/           # API route handlers
│   │   └── books.py   # Books and reviews endpoints
│   ├── core/          # Core configuration
│   ├── db/            # Database configuration
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic layer
│   │   ├── book_service.py  # Book operations
│   │   └── cache.py         # Redis cache service
│   └── tests/         # Test files
│       ├── conftest.py              # Test fixtures
│       ├── test_books_unit.py       # Unit tests
│       └── test_cache_integration.py # Integration tests
├── alembic/           # Database migrations
├── scripts/           # Utility scripts
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### Key Components

1. **FastAPI Application**: Modern, fast web framework with automatic API documentation
2. **SQLAlchemy ORM**: Database abstraction layer with relationship management
3. **Pydantic Schemas**: Data validation and serialization
4. **Redis Caching**: Performance optimization for frequently accessed data
5. **Alembic Migrations**: Database schema version control
6. **Pytest Testing**: Comprehensive test suite with fixtures and mocking

## ⚡ Performance Optimizations

1. **Database Indexing**: Optimized indexes on frequently queried columns
2. **Redis Caching**: Cache frequently accessed book lists with 5-minute TTL
3. **Connection Pooling**: Efficient database connection management
4. **Pagination**: Built-in pagination for large datasets
5. **Cache Invalidation**: Smart cache invalidation on data updates

## 🛡️ Error Handling

The service implements comprehensive error handling:

- **Graceful Cache Failures**: Service continues to work even if Redis is down
- **Database Connection Issues**: Proper error messages and logging
- **Input Validation**: Detailed validation error messages with Pydantic
- **404 Handling**: Clear messages for non-existent resources
- **Cache Miss Recovery**: Automatic fallback to database when cache fails

## 📊 Monitoring and Logging

- Structured logging with appropriate log levels
- Health check endpoint: `GET /health`
- Request/response logging for debugging
- Cache hit/miss logging for performance monitoring

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_USER | PostgreSQL username | kubesage |
| POSTGRES_PASSWORD | PostgreSQL password | linux |
| POSTGRES_HOST | PostgreSQL host | localhost |
| POSTGRES_PORT | PostgreSQL port | 5432 |
| POSTGRES_DB | PostgreSQL database name | book_review |
| REDIS_HOST | Redis host | localhost |
| REDIS_PORT | Redis port | 6379 |
| REDIS_PASSWORD | Redis password | None |
| REDIS_DB | Redis database number | 0 |
| DEBUG | Enable debug mode | true |

## 🚀 Production Deployment

### Docker Production Build

```bash
docker build -t book-review-service .
docker run -p 8000:8000 --env-file .env book-review-service
```

### Production Considerations

1. **Environment Variables**: Use secure methods to manage secrets
2. **Database**: Use managed PostgreSQL service (AWS RDS, Google Cloud SQL)
3. **Caching**: Use managed Redis service (AWS ElastiCache, Redis Cloud)
4. **Load Balancing**: Deploy behind a load balancer
5. **SSL/TLS**: Enable HTTPS in production
6. **Monitoring**: Implement application monitoring (Prometheus, DataDog)
7. **Logging**: Centralized logging (ELK stack, CloudWatch)

## 🤝 Contributing

1. Fork the repository from [https://github.com/Nisha16CGit/Book-Review](https://github.com/Nisha16CGit/Book-Review)
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features (unit and integration tests)
- Update documentation as needed
- Use type hints where possible
- Write descriptive commit messages

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Connect to database manually
docker-compose exec postgres psql -U kubesage -d book_review
```

#### Redis Connection Issues
```bash
# Check if Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Connect to Redis manually
docker-compose exec redis redis-cli
```

#### Migration Issues
```bash
# Check current migration status
alembic current

# Show migration history
alembic history

# Reset database (WARNING: This will delete all data)
alembic downgrade base
alembic upgrade head
```

#### Application Logs
```bash
# View application logs
docker-compose logs app

# Follow logs in real-time
docker-compose logs -f app
```

#### Test Issues
```bash
# Run tests with verbose output
pytest -v

# Run specific test file
pytest app/tests/test_books_unit.py -v

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## 📈 Performance Benchmarks

Expected performance metrics:
- **GET /books**: ~50ms (with cache), ~200ms (without cache)
- **POST /books**: ~100ms
- **GET /books/{id}/reviews**: ~30ms
- **POST /books/{id}/reviews**: ~80ms

## 🔐 Security Considerations

1. **Input Validation**: All inputs are validated using Pydantic
2. **SQL Injection**: Protected by SQLAlchemy ORM
3. **CORS**: Configured for development (restrict in production)
4. **Authentication**: Consider adding JWT authentication for production
5. **Authorization**: Implement role-based access control if needed

## 📝 API Rate Limiting (Future Enhancement)

Consider implementing rate limiting for production:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/books")
@limiter.limit("100/minute")
async def get_books(request: Request, ...):
    # endpoint logic
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the [GitHub repository](https://github.com/Nisha16CGit/Book-Review/issues)
- Check the troubleshooting section above
- Review the API documentation at `/docs`

## 📋 Changelog

### v1.0.0
- Initial release with core functionality
- Basic CRUD operations for books and reviews
- Redis caching implementation with cache miss handling
- Comprehensive test suite (unit and integration tests)
- Docker support with docker-compose
- Database migrations with Alembic
- Error handling and logging
- API documentation with Swagger/OpenAPI

---

## 🚀 Quick Commands

```bash
# Clone and setup
git clone https://github.com/Nisha16CGit/Book-Review.git
cd Book-Review

# Docker setup (recommended)
docker-compose up -d
docker-compose exec app alembic upgrade head

# Local setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Testing
pytest app/tests/test_books_unit.py -v
pytest app/tests/test_cache_integration.py -v
```

**Repository**: [https://github.com/Nisha16C/Book-Review.git](https://github.com/Nisha16C/Book-Review.git)

**Author**: Nisha Chaurasiya