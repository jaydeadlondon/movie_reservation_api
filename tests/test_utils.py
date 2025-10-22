from datetime import timedelta
from app.utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


class TestUtils:
    """Тесты для утилит"""

    def test_password_hashing(self):
        """Тест хеширования паролей"""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_password_verification_different_passwords(self):
        """Тест проверки разных паролей"""
        password1 = "password1"
        password2 = "password2"

        hashed1 = get_password_hash(password1)
        hashed2 = get_password_hash(password2)

        assert hashed1 != hashed2

        assert verify_password(password1, hashed1) is True
        assert verify_password(password2, hashed1) is False
        assert verify_password(password1, hashed2) is False
        assert verify_password(password2, hashed2) is True

    def test_create_access_token(self):
        """Тест создания токена доступа"""
        data = {"sub": "testuser", "role": "user"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        assert token.count(".") == 2

    def test_create_access_token_with_expires_delta(self):
        """Тест создания токена с кастомным временем истечения"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_valid(self):
        """Тест декодирования валидного токена"""
        data = {"sub": "testuser", "role": "user"}
        token = create_access_token(data)

        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "user"
        assert "exp" in decoded

    def test_decode_access_token_invalid(self):
        """Тест декодирования невалидного токена"""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)
        assert decoded is None

    def test_decode_access_token_malformed(self):
        """Тест декодирования некорректного токена"""
        malformed_token = "not.a.jwt.token"
        decoded = decode_access_token(malformed_token)
        assert decoded is None

    def test_token_expiration(self):
        """Тест истечения токена"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=1)
        token = create_access_token(data, expires_delta=expires_delta)

        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "testuser"

        import time

        time.sleep(2)

        decoded = decode_access_token(token)
        assert decoded is None
