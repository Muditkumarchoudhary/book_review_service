from sqlalchemy import Column, Integer, String, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from .database import Base

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    reviews = relationship("Review", back_populates="book")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), index=True)
    review_text = Column(Text)
    rating = Column(Integer)
    book = relationship("Book", back_populates="reviews")

    __table_args__ = (
        Index('ix_reviews_book_id', "book_id"),
    )

import redis
import json
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Book
from app.schemas import BookOut

router = APIRouter()

# Connect to Redis
def get_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        return r
    except redis.exceptions.ConnectionError:
        return None

@router.get("/books", response_model=list[BookOut])
def get_books():
    db: Session = SessionLocal()
    cache = get_redis()
    cache_key = "books:all"

    # Try cache first
    if cache:
        try:
            cached = cache.get(cache_key)
            if cached:
                return json.loads(cached)
        except redis.exceptions.ConnectionError:
            pass  # Cache is down, fallback to DB

    # Cache miss or cache down, fetch from DB
    books = db.query(Book).all()
    books_data = [BookOut.from_orm(b).dict() for b in books]

    # Try to populate cache
    if cache:
        try:
            cache.set(cache_key, json.dumps(books_data), ex=60)
        except redis.exceptions.ConnectionError:
            pass  # Cache is down

    return books_data
