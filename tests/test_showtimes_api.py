from fastapi import status
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.models.showtime import Showtime
from app.models.seat import Seat
from app.utils import get_password_hash, create_access_token


class TestShowtimesAPI:
    """Тесты для API сеансов"""

    def test_create_showtime_unauthorized(self, client, test_showtime_data):
        """Тест создания сеанса без авторизации"""
        response = client.post("/showtimes/", json=test_showtime_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_showtime_as_user(self, client, test_showtime_data, db_session):
        """Тест создания сеанса обычным пользователем"""
        movie = Movie(title="Test Movie", genre="Action", duration_minutes=120)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        user = User(
            email="user@example.com",
            username="user",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()

        token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}

        showtime_data = {
            "movie_id": movie.id,
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "hall_number": 1,
            "price": 15.50,
            "total_seats": 100,
        }

        response = client.post("/showtimes/", json=showtime_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in response.json()["detail"]

    def test_create_showtime_as_admin(self, client, test_showtime_data, db_session):
        """Тест создания сеанса администратором"""
        movie = Movie(title="Test Movie", genre="Action", duration_minutes=120)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("password123"),
            role=UserRole.ADMIN,
        )
        db_session.add(admin)
        db_session.commit()

        token = create_access_token(data={"sub": admin.username})
        headers = {"Authorization": f"Bearer {token}"}

        showtime_data = {
            "movie_id": movie.id,
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "hall_number": 1,
            "price": 15.50,
            "total_seats": 100,
        }

        response = client.post("/showtimes/", json=showtime_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert "message" in data
        assert "Showtime created with seats" in data["message"]

    def test_get_showtime_seats(self, client, db_session):
        """Тест получения мест сеанса"""
        movie = Movie(title="Test Movie", genre="Action", duration_minutes=120)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        showtime = Showtime(
            movie_id=movie.id,
            start_time=datetime.utcnow() + timedelta(days=1),
            hall_number=1,
            price=Decimal("15.50"),
            total_seats=100,
        )
        db_session.add(showtime)
        db_session.commit()
        db_session.refresh(showtime)

        seats = [
            Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=False),
            Seat(showtime_id=showtime.id, row="A", number=2, is_reserved=True),
            Seat(showtime_id=showtime.id, row="B", number=1, is_reserved=False),
        ]
        db_session.add_all(seats)
        db_session.commit()

        response = client.get(f"/showtimes/{showtime.id}/seats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

        seat_data = data[0]
        assert "id" in seat_data
        assert "row" in seat_data
        assert "number" in seat_data
        assert "is_reserved" in seat_data

    def test_get_showtime_seats_not_found(self, client):
        """Тест получения мест несуществующего сеанса"""
        response = client.get("/showtimes/999/seats")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Showtime not found" in response.json()["detail"]

    def test_get_available_seats(self, client, db_session):
        """Тест получения доступных мест"""
        movie = Movie(title="Test Movie", genre="Action", duration_minutes=120)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        showtime = Showtime(
            movie_id=movie.id,
            start_time=datetime.utcnow() + timedelta(days=1),
            hall_number=1,
            price=Decimal("15.50"),
            total_seats=100,
        )
        db_session.add(showtime)
        db_session.commit()
        db_session.refresh(showtime)

        seats = [
            Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=False),
            Seat(showtime_id=showtime.id, row="A", number=2, is_reserved=True),
            Seat(showtime_id=showtime.id, row="B", number=1, is_reserved=False),
            Seat(showtime_id=showtime.id, row="B", number=2, is_reserved=True),
        ]
        db_session.add_all(seats)
        db_session.commit()

        response = client.get(f"/showtimes/{showtime.id}/available-seats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 2
        for seat in data:
            assert seat["is_reserved"] is False

    def test_get_available_seats_not_found(self, client):
        """Тест получения доступных мест несуществующего сеанса"""
        response = client.get("/showtimes/999/available-seats")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
