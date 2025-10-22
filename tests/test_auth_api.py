import pytest
from fastapi import status
from app.models.user import User, UserRole
from app.utils import get_password_hash


class TestAuthAPI:
    """Тесты для API аутентификации"""

    def test_signup_success(self, client, test_user_data):
        """Тест успешной регистрации пользователя"""
        response = client.post("/auth/signup", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["role"] == UserRole.USER.value
        assert "id" in data
        assert "password" not in data

    def test_signup_duplicate_email(self, client, test_user_data, db_session):
        """Тест регистрации с дублирующимся email"""
        user = User(
            email=test_user_data["email"],
            username="existinguser",
            hashed_password=get_password_hash(test_user_data["password"]),
        )
        db_session.add(user)
        db_session.commit()

        response = client.post("/auth/signup", json=test_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_signup_duplicate_username(self, client, test_user_data, db_session):
        """Тест регистрации с дублирующимся username"""
        user = User(
            email="different@example.com",
            username=test_user_data["username"],
            hashed_password=get_password_hash(test_user_data["password"]),
        )
        db_session.add(user)
        db_session.commit()

        response = client.post("/auth/signup", json=test_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response.json()["detail"]

    def test_login_success(self, client, test_user_data, db_session):
        """Тест успешного входа"""
        user = User(
            email=test_user_data["email"],
            username=test_user_data["username"],
            hashed_password=get_password_hash(test_user_data["password"]),
        )
        db_session.add(user)
        db_session.commit()

        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client, test_user_data):
        """Тест входа с неверным username"""
        login_data = {"username": "nonexistent", "password": test_user_data["password"]}
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_invalid_password(self, client, test_user_data, db_session):
        """Тест входа с неверным паролем"""
        user = User(
            email=test_user_data["email"],
            username=test_user_data["username"],
            hashed_password=get_password_hash(test_user_data["password"]),
        )
        db_session.add(user)
        db_session.commit()

        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword",
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_signup_invalid_email(self, client):
        """Тест регистрации с невалидным email"""
        invalid_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "testpassword123",
        }
        response = client.post("/auth/signup", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
