#!/usr/bin/env python3
"""
Database initialization script
"""
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.core.config import settings
from app.db.database import Base
from app.models import Book, Review

def init_database():
    """Initialize the database with tables"""
    engine = create_engine(settings.database_url)
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()