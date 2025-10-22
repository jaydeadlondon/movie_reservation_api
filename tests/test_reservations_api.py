from fastapi import status
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.models.showtime import Showtime
from app.models.seat import Seat
from app.models.reservation import Reservation, ReservationStatus
from app.utils import get_password_hash, create_access_token


class TestReservationsAPI:
    """Тесты для API бронирований"""

    def test_create_reservation_unauthorized(self, client):
        """Тест создания бронирования без авторизации"""
        reservation_data = {"showtime_id": 1, "seat_ids": [1, 2]}
        response = client.post("/reservations/", json=reservation_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_reservation_success(self, client, db_session):
        """Тест успешного создания бронирования"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

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
            Seat(showtime_id=showtime.id, row="A", number=2, is_reserved=False),
        ]
        db_session.add_all(seats)
        db_session.commit()
        db_session.refresh(seats[0])
        db_session.refresh(seats[1])

        token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}

        reservation_data = {
            "showtime_id": showtime.id,
            "seat_ids": [seats[0].id, seats[1].id],
        }

        response = client.post("/reservations/", json=reservation_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data) == 2

        db_session.refresh(seats[0])
        db_session.refresh(seats[1])
        assert seats[0].is_reserved is True
        assert seats[1].is_reserved is True

    def test_create_reservation_showtime_not_found(self, client, db_session):
        """Тест создания бронирования для несуществующего сеанса"""
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

        reservation_data = {"showtime_id": 999, "seat_ids": [1, 2]}

        response = client.post("/reservations/", json=reservation_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Showtime not found" in response.json()["detail"]

    def test_create_reservation_past_showtime(self, client, db_session):
        """Тест создания бронирования для прошедшего сеанса"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        movie = Movie(title="Test Movie", genre="Action", duration_minutes=120)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        showtime = Showtime(
            movie_id=movie.id,
            start_time=datetime.utcnow() - timedelta(days=1),
            hall_number=1,
            price=Decimal("15.50"),
            total_seats=100,
        )
        db_session.add(showtime)
        db_session.commit()
        db_session.refresh(showtime)

        seat = Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=False)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)

        token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}

        reservation_data = {"showtime_id": showtime.id, "seat_ids": [seat.id]}

        response = client.post("/reservations/", json=reservation_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot reserve seats for past showtimes" in response.json()["detail"]

    def test_create_reservation_seat_already_reserved(self, client, db_session):
        """Тест создания бронирования для уже забронированного места"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

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

        seat = Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=True)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)

        token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}

        reservation_data = {"showtime_id": showtime.id, "seat_ids": [seat.id]}

        response = client.post("/reservations/", json=reservation_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Seats already reserved" in response.json()["detail"]

    def test_get_my_reservations_unauthorized(self, client):
        """Тест получения своих бронирований без авторизации"""
        response = client.get("/reservations/my")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_my_reservations_success(self, client, db_session):
        """Тест успешного получения своих бронирований"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

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

        seat = Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=True)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)

        reservation = Reservation(
            user_id=user.id,
            showtime_id=showtime.id,
            seat_id=seat.id,
            status=ReservationStatus.CONFIRMED,
        )
        db_session.add(reservation)
        db_session.commit()

        token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/reservations/my", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["movie_title"] == "Test Movie"
        assert data[0]["seat_row"] == "A"
        assert data[0]["seat_number"] == 1
        assert data[0]["status"] == ReservationStatus.CONFIRMED.value

    def test_cancel_reservation_unauthorized(self, client):
        """Тест отмены бронирования без авторизации"""
        response = client.delete("/reservations/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cancel_reservation_success(self, client, db_session):
        """Тест успешной отмены бронирования"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

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

        seat = Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=True)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)

        reservation = Reservation(
            user_id=user.id,
            showtime_id=showtime.id,
            seat_id=seat.id,
            status=ReservationStatus.CONFIRMED,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.delete(f"/reservations/{reservation.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        db_session.refresh(seat)
        assert seat.is_reserved is False

        db_session.refresh(reservation)
        assert reservation.status == ReservationStatus.CANCELLED

    def test_cancel_reservation_not_found(self, client, db_session):
        """Тест отмены несуществующего бронирования"""
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

        response = client.delete("/reservations/999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Reservation not found" in response.json()["detail"]

    def test_cancel_reservation_not_owner(self, client, db_session):
        """Тест отмены чужого бронирования"""
        user1 = User(
            email="user1@example.com",
            username="user1",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)

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

        seat = Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=True)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)

        reservation = Reservation(
            user_id=user1.id,
            showtime_id=showtime.id,
            seat_id=seat.id,
            status=ReservationStatus.CONFIRMED,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        token = create_access_token(data={"sub": user2.username})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.delete(f"/reservations/{reservation.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not your reservation" in response.json()["detail"]
