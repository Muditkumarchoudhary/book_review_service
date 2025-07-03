from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
from app.models import get_redis

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/books", response_model=list[schemas.BookOut])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

@router.post("/books", response_model=schemas.BookOut)
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.get("/books/{book_id}/reviews", response_model=list[schemas.ReviewOut])
def get_reviews(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.reviews

@router.post("/books/{book_id}/reviews", response_model=schemas.ReviewOut)
def add_review(book_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db_review = models.Review(
        book_id=book_id,
        review_text=review.comment,  # map comment to review_text
        rating=5  # or get from review if you add it to the schema
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.get("/books", response_model=list[schemas.BookOut])
def get_books(db: Session = Depends(get_db)):
    cache = get_redis()
    cache_key = "books:all"

    # Try cache first
    if cache:
        try:
            cached_books = cache.get(cache_key)
            if cached_books:
                import json
                return [schemas.BookOut(**b) for b in json.loads(cached_books)]
        except Exception:
            pass  # Cache is down or error

    # Cache miss or cache down, fetch from DB
    books = db.query(models.Book).all()
    books_data = [schemas.BookOut.from_orm(b).dict() for b in books]

    # Try to populate cache
    if cache:
        try:
            import json
            cache.set(cache_key, json.dumps(books_data), ex=60)
        except Exception:
            pass  # Cache is down

    return books_data
