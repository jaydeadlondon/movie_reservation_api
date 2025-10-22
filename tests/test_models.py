import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.models.showtime import Showtime
from app.models.seat import Seat
from app.models.reservation import Reservation, ReservationStatus


class TestUserModel:
    """Тесты для модели User"""

    def test_user_creation(self, db_session):
        """Тест создания пользователя"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == UserRole.USER
        assert user.is_active is True

    def test_user_default_values(self, db_session):
        """Тест значений по умолчанию для пользователя"""
        user = User(
            email="test2@example.com",
            username="testuser2",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.role == UserRole.USER
        assert user.is_active is True


class TestMovieModel:
    """Тесты для модели Movie"""

    def test_movie_creation(self, db_session):
        """Тест создания фильма"""
        movie = Movie(
            title="Test Movie",
            description="A test movie",
            poster_url="https://example.com/poster.jpg",
            genre="Action",
            duration_minutes=120,
        )
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        assert movie.id is not None
        assert movie.title == "Test Movie"
        assert movie.description == "A test movie"
        assert movie.genre == "Action"
        assert movie.duration_minutes == 120


class TestShowtimeModel:
    """Тесты для модели Showtime"""

    def test_showtime_creation(self, db_session):
        """Тест создания сеанса"""
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

        assert showtime.id is not None
        assert showtime.movie_id == movie.id
        assert showtime.hall_number == 1
        assert showtime.price == Decimal("15.50")
        assert showtime.total_seats == 100


class TestSeatModel:
    """Тесты для модели Seat"""

    def test_seat_creation(self, db_session):
        """Тест создания места"""
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

        seat = Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=False)
        db_session.add(seat)
        db_session.commit()
        db_session.refresh(seat)

        assert seat.id is not None
        assert seat.showtime_id == showtime.id
        assert seat.row == "A"
        assert seat.number == 1
        assert seat.is_reserved is False


class TestReservationModel:
    """Тесты для модели Reservation"""

    def test_reservation_creation(self, db_session):
        """Тест создания бронирования"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
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

        seat = Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=False)
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

        assert reservation.id is not None
        assert reservation.user_id == user.id
        assert reservation.showtime_id == showtime.id
        assert reservation.seat_id == seat.id
        assert reservation.status == ReservationStatus.CONFIRMED
        assert reservation.created_at is not None


class TestModelRelationships:
    """Тесты для связей между моделями"""

    def test_user_reservations_relationship(self, db_session):
        """Тест связи пользователь-бронирования"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
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

        seat = Seat(showtime_id=showtime.id, row="A", number=1, is_reserved=False)
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

        assert len(user.reservations) == 1
        assert user.reservations[0].id == reservation.id

    def test_movie_showtimes_relationship(self, db_session):
        """Тест связи фильм-сеансы"""
        movie = Movie(title="Test Movie", genre="Action", duration_minutes=120)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        showtime1 = Showtime(
            movie_id=movie.id,
            start_time=datetime.utcnow() + timedelta(days=1),
            hall_number=1,
            price=Decimal("15.50"),
            total_seats=100,
        )
        showtime2 = Showtime(
            movie_id=movie.id,
            start_time=datetime.utcnow() + timedelta(days=2),
            hall_number=2,
            price=Decimal("18.00"),
            total_seats=150,
        )
        db_session.add_all([showtime1, showtime2])
        db_session.commit()
        db_session.refresh(movie)

        assert len(movie.showtimes) == 2
        assert movie.showtimes[0].id == showtime1.id
        assert movie.showtimes[1].id == showtime2.id
