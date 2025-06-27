from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.schemas.book import Book, BookCreate
from app.schemas.review import Review, ReviewCreate
from app.services.book_service import BookService
from app.services.cache import cache_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=List[Book])
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all books with pagination support.
    
    - **skip**: Number of books to skip (for pagination)
    - **limit**: Maximum number of books to return
    """
    cache_key = f"books:list:{skip}:{limit}"
    
    try:
        # First attempt to read from cache
        cached_books = cache_service.get(cache_key)
        if cached_books is not None:
            logger.info(f"Returning {len(cached_books)} books from cache")
            return cached_books
        
        # Cache miss - read from database
        logger.info("Cache miss, fetching books from database")
        books = BookService.get_books(db, skip=skip, limit=limit)
        
        # Convert SQLAlchemy objects to dictionaries for caching
        books_data = []
        for book in books:
            book_dict = {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "description": book.description,
                "published_year": book.published_year,
                "created_at": book.created_at.isoformat() if book.created_at else None,
                "updated_at": book.updated_at.isoformat() if book.updated_at else None
            }
            books_data.append(book_dict)
        
        # Populate cache with fetched data
        cache_success = cache_service.set(cache_key, books_data, expire=300)
        if cache_success:
            logger.info(f"Successfully cached {len(books_data)} books")
        else:
            logger.warning("Failed to cache books data")
        
        return books
        
    except Exception as e:
        # Proper error handling - if cache is down, still serve from database
        logger.error(f"Error in get_books: {str(e)}")
        
        # If there's a cache-related error, try to fetch from database directly
        try:
            logger.info("Attempting to fetch books directly from database due to cache error")
            books = BookService.get_books(db, skip=skip, limit=limit)
            return books
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(db_error)}")

@router.post("/", response_model=Book, status_code=201)
async def create_book(
    book: BookCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new book.
    
    - **title**: Book title (required)
    - **author**: Book author (required)
    - **isbn**: ISBN number (optional, min 10 characters if provided)
    - **description**: Book description (optional)
    - **published_year**: Year of publication (optional)
    """
    logger.info(f"Attempting to create book: {book.dict()}")
    
    try:
        logger.info("Calling BookService.create_book")
        new_book = BookService.create_book(db, book)
        logger.info(f"Successfully created book with ID: {new_book.id}")
        
        # Invalidate relevant cache entries after creating a new book
        try:
            # Simple cache invalidation - delete common cache keys
            cache_keys_to_invalidate = [
                "books:list:0:100",  # Default pagination
                "books:list:0:10",   # Common small pagination
                "books:list:0:50"    # Common medium pagination
            ]
            
            for cache_key in cache_keys_to_invalidate:
                cache_service.delete(cache_key)
                
            logger.info("Cache invalidated after book creation")
        except Exception as cache_error:
            logger.warning(f"Cache invalidation failed: {cache_error}")
            # Don't fail the request if cache invalidation fails
        
        return new_book
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        db.rollback()
        
        if "duplicate key value violates unique constraint" in str(e):
            if "ix_books_isbn" in str(e):
                raise HTTPException(status_code=400, detail="A book with this ISBN already exists")
            else:
                raise HTTPException(status_code=400, detail="A book with these details already exists")
        
        raise HTTPException(status_code=400, detail="Database constraint violation")
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create book")

@router.get("/{book_id}/reviews", response_model=List[Review])
async def get_book_reviews(
    book_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all reviews for a specific book.
    
    - **book_id**: ID of the book
    - **skip**: Number of reviews to skip (for pagination)
    - **limit**: Maximum number of reviews to return
    """
    # Check if book exists
    book = BookService.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        reviews = BookService.get_book_reviews(db, book_id, skip=skip, limit=limit)
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{book_id}/reviews", response_model=Review, status_code=201)
async def create_book_review(
    book_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new review for a specific book.
    
    - **book_id**: ID of the book
    - **reviewer_name**: Name of the reviewer (required)
    - **rating**: Rating from 1 to 5 stars (required)
    - **comment**: Review comment (optional)
    """
    # Check if book exists
    book = BookService.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        return BookService.create_review(db, book_id, review)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")