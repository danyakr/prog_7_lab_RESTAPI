from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, BookDB
from auth import verify_api_key  # <-- Добавлен импорт для аутентификации

# Создание экземпляра приложения FastAPI
app = FastAPI(
    title="Books API",
    description="REST API для управления библиотекой книг на SQLAlchemy",
    version="1.0.0"
)


# Модель данных для книги (Pydantic схема)
class Book(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200, description="Название книги")
    author: str = Field(..., min_length=1, max_length=100, description="Автор книги")
    year: int = Field(..., ge=1000, le=datetime.now().year, description="Год издания")
    isbn: Optional[str] = Field(None, min_length=10, max_length=13, description="ISBN книги")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Мастер и Маргарита",
                "author": "Михаил Булгаков",
                "year": 1967,
                "isbn": "9785170123456"
            }
        }
        # Важно для работы с SQLAlchemy ORM моделями
        from_attributes = True

    # Модель для обновления книги (все поля опциональны)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)


# Корневой эндпоинт
@app.get("/", tags=["Root"])
async def root():
    """
    Корневой эндпоинт API.
    Возвращает приветственное сообщение и ссылки на документацию.
    """
    return {
        "message": "Добро пожаловать в Books API!",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# --- ЭНДПОИНТЫ ЧТЕНИЯ (НЕ ТРЕБУЮТ АУТЕНТИФИКАЦИИ) ---
@app.get("/api/books", response_model=List[Book], tags=["Books"])
async def get_books(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 10,
        author: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
):
    """
    Получить список книг с фильтрацией и пагинацией из базы данных.
    """

    query = db.query(BookDB)

    if author:
        query = query.filter(BookDB.author.ilike(f"%{author}%"))

    if year_from:
        query = query.filter(BookDB.year >= year_from)

    if year_to:
        query = query.filter(BookDB.year <= year_to)

    books = query.offset(skip).limit(limit).all()

    return books


@app.get("/api/books/stats", tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)):
    """
    Получить статистику по книгам из базы данных.
    """
    all_books = db.query(BookDB).all()
    total_books = len(all_books)
    authors = Counter(book.author for book in all_books)
    centuries = Counter(book.year // 100 + 1 for book in all_books)

    return {
        "total_books": total_books,
        "books_by_author": dict(authors),
        "books_by_century": {
            f"{century} век": count
            for century, count in centuries.items()
        }
    }


@app.get("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """
    Получить книгу по ID из базы данных.
    """
    book = db.query(BookDB).filter(BookDB.id == book_id).first()

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )
    return book


# --- ЭНДПОИНТЫ ЗАПИСИ (ТРЕБУЮТ АУТЕНТИФИКАЦИИ) ---

# POST /api/books - Создание новой книги
@app.post("/api/books", response_model=Book, status_code=status.HTTP_201_CREATED,
          tags=["Books"])
async def create_book(
        book: Book,
        db: Session = Depends(get_db),
        api_key: str = Depends(verify_api_key)  # <-- Защита: требуется API ключ
):
    """
    Создать новую книгу в базе данных (требуется аутентификация).
    """
    db_book = BookDB(**book.model_dump(exclude={"id"}))

    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


# PUT /api/books/{book_id} - Полное обновление книги
@app.put("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def update_book(
        book_id: int,
        updated_book: Book,
        db: Session = Depends(get_db),
        api_key: str = Depends(verify_api_key)  # <-- Защита: требуется API ключ
):
    """
    Полностью обновить информацию о книге в базе данных (требуется аутентификация).
    """
    db_book = db.query(BookDB).filter(BookDB.id == book_id).first()

    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )

    for field, value in updated_book.model_dump(exclude={"id"}).items():
        setattr(db_book, field, value)

    db.commit()
    db.refresh(db_book)
    return db_book


# PATCH /api/books/{book_id} - Частичное обновление книги
@app.patch("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def partial_update_book(
        book_id: int,
        book_update: BookUpdate,
        db: Session = Depends(get_db),
        api_key: str = Depends(verify_api_key)  # <-- Защита: требуется API ключ
):
    """
    Частично обновить информацию о книге в базе данных (требуется аутентификация).
    """
    db_book = db.query(BookDB).filter(BookDB.id == book_id).first()

    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )

    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_book, field) and value is not None:
            setattr(db_book, field, value)

    db.commit()
    db.refresh(db_book)
    return db_book


# DELETE /api/books/{book_id} - Удаление книги
@app.delete("/api/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
async def delete_book(
        book_id: int,
        db: Session = Depends(get_db),
        api_key: str = Depends(verify_api_key)  # <-- Защита: требуется API ключ
):
    """
    Удалить книгу по ID из базы данных (требуется аутентификация).
    """
    db_book = db.query(BookDB).filter(BookDB.id == book_id).first()

    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )

    db.delete(db_book)
    db.commit()
    return


# Точка входа для запуска приложения
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
