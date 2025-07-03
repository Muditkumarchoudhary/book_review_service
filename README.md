# book_review_service
A FastAPI-based web service for managing books and their reviews, featuring:
- SQLite (or PostgreSQL) with SQLAlchemy ORM
- Alembic migrations
- Redis cache integration (mockable for tests)
- Pydantic v2 support
- Automated unit and integration tests

---

# Features

- Books: Add, list, and review books.
- Reviews: Add and list reviews for each book.
- Caching: Uses Redis to cache book listings for performance.
- Migrations: Database schema managed with Alembic.
- Testing: Unit and integration tests using pytest.

---

# Requirements

- Python 3.10+
- [Redis](https://redis.io/) (for caching; optional for tests)
- SQLite (default) or PostgreSQL
- [Git](https://git-scm.com/)

---

# Setup

# 1. Clone the repository

git clone https://github.com/Muditkumarchoudhary/book_review_service.git

cd book_review_service


# 2. Create and activate a virtual environment

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/Mac:
source venv/bin/activate

# 3. Install dependencies

pip install -r requirements.txt

# Database Migrations

# 1. Initialize Alembic (if not already done)

alembic init alembic


# 2. Configure Alembic

Edit `alembic.ini` and set your database URL, e.g.:
sqlalchemy.url = sqlite:///./books.db


# 3. Generate and apply migrations

alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Running the Service

uvicorn app.main:app --reload

- Visit (http://127.0.0.1:8000/docs) for the interactive API docs.


# Redis Cache

- The `/books` endpoint uses Redis to cache the list of books.
- If Redis is down, the service will fall back to the database and continue to work.
- For local development, you can install Redis from [https://redis.io/download](https://redis.io/download).

# Running Tests

pytest -v

- Tests are in the tests/ directory.
- Includes unit tests for endpoints and an integration test for cache-miss.


# Project Structure

book_review_service/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── routes.py
│
├── tests/
│   └── test_books.py
│
├── alembic/
│   └── ... (migration scripts)
│
├── requirements.txt
├── .gitignore
├── README.md


# Example API Usage

-> List all books:  
  `GET /books`

-> Add a new book:  
  POST /books`  
  {
    "title": "My Book",
    "author": "Author Name"
  }
  

-> List reviews for a book:  
   GET /books/{book_id}/reviews

-> Add a review to a book:  
  POST /books/{book_id}/reviews  
  {
    "reviewer": "Alice",
    "comment": "Great read!"
  }

# Notes

- To use PostgreSQL, update the database URL in both `app/database.py` and `alembic.ini`.
- Redis is optional for running tests (cache is mocked in tests).
- For Pydantic v2, all models use `model_config = ConfigDict(from_attributes=True)`.
- The `venv/` directory is excluded from version control via `.gitignore`.

# License

MIT
