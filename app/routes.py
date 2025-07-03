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
    # Map each Review to ReviewOut
    return [
        schemas.ReviewOut(
            id=review.id,
            reviewer="",  # or set to a default or fetch if you add this field to the model
            comment=review.review_text
        )
        for review in book.reviews
    ]

@router.post("/books/{book_id}/reviews", response_model=schemas.ReviewOut)
def add_review(book_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db_review = models.Review(
        book_id=book_id,
        review_text=review.comment,
        rating=5
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    # Return a ReviewOut with the expected fields
    return schemas.ReviewOut(
        id=db_review.id,
        reviewer=review.reviewer,
        comment=review.comment
    )

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
    books_data = []
    for b in books:
        books_data.append(
            schemas.BookOut(
                id=b.id,
                title=b.title,
                author=b.author,
                reviews=[
                    schemas.ReviewOut(
                        id=r.id,
                        reviewer="",  # or r.reviewer if you add it to the model
                        comment=r.review_text
                    )
                    for r in b.reviews
                ]
            )
        )

    # Try to populate cache
    if cache:
        try:
            import json
            cache.set(cache_key, json.dumps([book.model_dump() for book in books_data]), ex=60)
        except Exception:
            pass  # Cache is down

    return books_data
