import pytest
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.dependencies import get_current_user, require_admin
from app.utils import create_access_token


class TestDependencies:
    """Тесты для зависимостей"""

    def test_get_current_user_valid_token(self, db_session):
        """Тест получения текущего пользователя с валидным токеном"""
        user = User(
            email="user@example.com",
            username="testuser",
            hashed_password="hashed_password",
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = create_access_token(data={"sub": user.username})

        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        current_user = get_current_user(credentials, db_session)

        assert current_user.id == user.id
        assert current_user.username == user.username
        assert current_user.email == user.email

    def test_get_current_user_invalid_token(self, db_session):
        """Тест получения текущего пользователя с невалидным токеном"""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_token"
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication credentials" in exc_info.value.detail

    def test_get_current_user_nonexistent_user(self, db_session):
        """Тест получения несуществующего пользователя"""
        token = create_access_token(data={"sub": "nonexistent_user"})

        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User not found" in exc_info.value.detail

    def test_get_current_user_missing_sub(self, db_session):
        """Тест получения пользователя с токеном без sub"""
        token = create_access_token(data={"role": "user"})

        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication credentials" in exc_info.value.detail

    def test_require_admin_with_admin_user(self, db_session):
        """Тест проверки прав администратора для админа"""
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password="hashed_password",
            role=UserRole.ADMIN,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)

        token = create_access_token(data={"sub": admin.username})

        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        current_user = get_current_user(credentials, db_session)
        admin_user = require_admin(current_user)

        assert admin_user.id == admin.id
        assert admin_user.role == UserRole.ADMIN

    def test_require_admin_with_regular_user(self, db_session):
        """Тест проверки прав администратора для обычного пользователя"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed_password",
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = create_access_token(data={"sub": user.username})

        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        current_user = get_current_user(credentials, db_session)

        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in exc_info.value.detail
