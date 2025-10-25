from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. Настройка подключения к базе данных SQLite
# Файл books.db будет создан в корневой папке проекта
SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"

# connect_args={"check_same_thread": False} требуется только для SQLite,
# чтобы разрешить множественные запросы в одном потоке (как в FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 2. Настройка сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Базовый класс для моделей
Base = declarative_base()


# 4. Модель таблицы Book (ORM)
class BookDB(Base):
    """
    Модель базы данных для хранения книг.
    Соответствует таблице 'books' в SQLite.
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    isbn = Column(String(13), nullable=True)


# 5. Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)


# 6. Функция для инициализации базы данных стартовыми данными (вызывается один раз)
def initialize_db_data(db: Session):
    """
    Добавляет начальные книги, если таблица пуста.
    """
    # Проверяем, пуста ли таблица
    if db.query(BookDB).count() == 0:
        initial_books = [
            {"title": "Война и мир", "author": "Лев Толстой", "year": 1869, "isbn": "9785170987654"},
            {"title": "Преступление и наказание", "author": "Федор Достоевский", "year": 1866, "isbn": "9785170876543"},
            {"title": "Евгений Онегин", "author": "Александр Пушкин", "year": 1833, "isbn": "9785170765432"}
        ]

        for book_data in initial_books:
            db_book = BookDB(**book_data)
            db.add(db_book)

        db.commit()


# Запускаем инициализацию данных сразу после создания таблиц
# Мы создаем временную сессию для этой операции
try:
    db = SessionLocal()
    initialize_db_data(db)
finally:
    db.close()


# 7. Функция-зависимость для получения сессии базы данных
def get_db():
    """
    Предоставляет сессию базы данных для каждого запроса.
    Гарантирует закрытие сессии после завершения запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
