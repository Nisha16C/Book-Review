from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    description: Optional[str] = None
    published_year: Optional[int] = Field(None, ge=1000, le=2024)

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    description: Optional[str] = None
    published_year: Optional[int] = Field(None, ge=1000, le=2024)

class Book(BookBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BookWithReviews(Book):
    reviews: List['Review'] = []