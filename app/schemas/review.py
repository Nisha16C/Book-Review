from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    reviewer_name: str = Field(..., min_length=1, max_length=255)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    reviewer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class Review(ReviewBase):
    id: int
    book_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Update forward reference
from app.schemas.book import BookWithReviews
BookWithReviews.model_rebuild()