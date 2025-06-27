from sqlalchemy.orm import Session
from app.models.book import Book, Review
from app.schemas.book import BookCreate
from app.schemas.review import ReviewCreate
from typing import List

class BookService:
    @staticmethod
    def get_books(db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
        return db.query(Book).offset(skip).limit(limit).all()

    @staticmethod
    def get_book(db: Session, book_id: int) -> Book:
        return db.query(Book).filter(Book.id == book_id).first()

    @staticmethod
    def create_book(db: Session, book: BookCreate) -> Book:
        book_data = book.model_dump() if hasattr(book, 'model_dump') else book.dict()
        db_book = Book(**book_data)
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book

    @staticmethod
    def get_book_reviews(db: Session, book_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return db.query(Review).filter(Review.book_id == book_id).offset(skip).limit(limit).all()

    @staticmethod
    def create_review(db: Session, book_id: int, review: ReviewCreate) -> Review:
        review_data = review.model_dump() if hasattr(review, 'model_dump') else review.dict()
        db_review = Review(**review_data, book_id=book_id)
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review