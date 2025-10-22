import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_movie_reservation.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Создает новую сессию базы данных для каждого теста"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Создает тестовый клиент FastAPI"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Тестовые данные пользователя"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }


@pytest.fixture
def test_movie_data():
    """Тестовые данные фильма"""
    return {
        "title": "Test Movie",
        "description": "A test movie description",
        "poster_url": "https://example.com/poster.jpg",
        "genre": "Action",
        "duration_minutes": 120,
    }


@pytest.fixture
def test_showtime_data():
    """Тестовые данные сеанса"""
    from datetime import datetime, timedelta

    return {
        "movie_id": 1,
        "start_time": datetime.utcnow() + timedelta(days=1),
        "hall_number": 1,
        "price": 15.50,
        "total_seats": 100,
    }


@pytest.fixture
def admin_user_data():
    """Тестовые данные администратора"""
    return {
        "email": "admin@example.com",
        "username": "admin",
        "password": "adminpassword123",
    }
