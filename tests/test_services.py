import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.models.showtime import Showtime
from app.models.seat import Seat
from app.models.reservation import Reservation, ReservationStatus
from app.services.movie_service import MovieService
from app.services.reservation_service import ReservationService


class TestMovieService:
    """Тесты для сервиса фильмов"""

    def test_create_showtime_with_seats(self, db_session):
        """Тест создания сеанса с местами"""
        movie = Movie(title="Test Movie", genre="Action", duration_minutes=120)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        showtime = MovieService.create_showtime_with_seats(
            db=db_session,
            movie_id=movie.id,
            start_time=datetime.utcnow() + timedelta(days=1),
            hall_number=1,
            price=15.50,
            total_seats=100,
        )

        assert showtime.id is not None
        assert showtime.movie_id == movie.id
        assert showtime.hall_number == 1
        assert showtime.price == Decimal("15.50")
        assert showtime.total_seats == 100

        seats = db_session.query(Seat).filter(Seat.showtime_id == showtime.id).all()
        assert len(seats) == 100

        rows = set(seat.row for seat in seats)
        assert len(rows) == 10
        assert rows == {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}

        for row in rows:
            row_seats = [seat for seat in seats if seat.row == row]
            assert len(row_seats) == 10
            numbers = [seat.number for seat in row_seats]
            assert numbers == list(range(1, 11))

    def test_get_movies_with_showtimes(self, db_session):
        """Тест получения фильмов с сеансами"""
        movie = Movie(title="Test Movie", genre="Action", duration_minutes=120)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        today = date.today()
        tomorrow = today + timedelta(days=1)

        showtime_today = Showtime(
            movie_id=movie.id,
            start_time=datetime.combine(today, datetime.min.time())
            + timedelta(hours=10),
            hall_number=1,
            price=Decimal("15.50"),
            total_seats=100,
        )
        showtime_tomorrow = Showtime(
            movie_id=movie.id,
            start_time=datetime.combine(tomorrow, datetime.min.time())
            + timedelta(hours=10),
            hall_number=1,
            price=Decimal("15.50"),
            total_seats=100,
        )
        db_session.add_all([showtime_today, showtime_tomorrow])
        db_session.commit()

        result = MovieService.get_movies_with_showtimes(db_session, today)

        assert len(result) == 1
        assert result[0]["movie"].title == "Test Movie"
        assert len(result[0]["showtimes"]) == 1
        assert result[0]["showtimes"][0]["hall_number"] == 1
        assert result[0]["showtimes"][0]["available_seats"] == 100

    def test_get_available_seats(self, db_session):
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

        available_seats = MovieService.get_available_seats(db_session, showtime.id)

        assert len(available_seats) == 2
        for seat in available_seats:
            assert seat.is_reserved is False


class TestReservationService:
    """Тесты для сервиса бронирований"""

    def test_reserve_seats_success(self, db_session):
        """Тест успешного бронирования мест"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed_password",
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

        reservations = ReservationService.reserve_seats(
            db=db_session,
            user_id=user.id,
            showtime_id=showtime.id,
            seat_ids=[seats[0].id, seats[1].id],
        )

        assert len(reservations) == 2
        assert reservations[0].user_id == user.id
        assert reservations[0].showtime_id == showtime.id
        assert reservations[0].status == ReservationStatus.CONFIRMED

        db_session.refresh(seats[0])
        db_session.refresh(seats[1])
        assert seats[0].is_reserved is True
        assert seats[1].is_reserved is True

    def test_reserve_seats_showtime_not_found(self, db_session):
        """Тест бронирования мест для несуществующего сеанса"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed_password",
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        with pytest.raises(HTTPException) as exc_info:
            ReservationService.reserve_seats(
                db=db_session, user_id=user.id, showtime_id=999, seat_ids=[1, 2]
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Showtime not found" in exc_info.value.detail

    def test_reserve_seats_past_showtime(self, db_session):
        """Тест бронирования мест для прошедшего сеанса"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed_password",
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

        with pytest.raises(HTTPException) as exc_info:
            ReservationService.reserve_seats(
                db=db_session,
                user_id=user.id,
                showtime_id=showtime.id,
                seat_ids=[seat.id],
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot reserve seats for past showtimes" in exc_info.value.detail

    def test_reserve_seats_already_reserved(self, db_session):
        """Тест бронирования уже забронированных мест"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed_password",
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

        with pytest.raises(HTTPException) as exc_info:
            ReservationService.reserve_seats(
                db=db_session,
                user_id=user.id,
                showtime_id=showtime.id,
                seat_ids=[seat.id],
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Seats already reserved" in exc_info.value.detail

    def test_cancel_reservation_success(self, db_session):
        """Тест успешной отмены бронирования"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed_password",
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

        cancelled_reservation = ReservationService.cancel_reservation(
            db=db_session, reservation_id=reservation.id, user_id=user.id
        )

        assert cancelled_reservation.status == ReservationStatus.CANCELLED

        db_session.refresh(seat)
        assert seat.is_reserved is False

    def test_cancel_reservation_not_found(self, db_session):
        """Тест отмены несуществующего бронирования"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed_password",
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        with pytest.raises(HTTPException) as exc_info:
            ReservationService.cancel_reservation(
                db=db_session, reservation_id=999, user_id=user.id
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Reservation not found" in exc_info.value.detail

    def test_cancel_reservation_not_owner(self, db_session):
        """Тест отмены чужого бронирования"""
        user1 = User(
            email="user1@example.com",
            username="user1",
            hashed_password="hashed_password",
            role=UserRole.USER,
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password="hashed_password",
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

        with pytest.raises(HTTPException) as exc_info:
            ReservationService.cancel_reservation(
                db=db_session, reservation_id=reservation.id, user_id=user2.id
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Not your reservation" in exc_info.value.detail

    def test_get_user_reservations(self, db_session):
        """Тест получения бронирований пользователя"""
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed_password",
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        movie = Movie(title="Test Movie", genre="Action", duration_minutes=120)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        future_showtime = Showtime(
            movie_id=movie.id,
            start_time=datetime.utcnow() + timedelta(days=1),
            hall_number=1,
            price=Decimal("15.50"),
            total_seats=100,
        )
        past_showtime = Showtime(
            movie_id=movie.id,
            start_time=datetime.utcnow() - timedelta(days=1),
            hall_number=2,
            price=Decimal("15.50"),
            total_seats=100,
        )
        db_session.add_all([future_showtime, past_showtime])
        db_session.commit()
        db_session.refresh(future_showtime)
        db_session.refresh(past_showtime)

        future_seat = Seat(
            showtime_id=future_showtime.id, row="A", number=1, is_reserved=True
        )
        past_seat = Seat(
            showtime_id=past_showtime.id, row="A", number=1, is_reserved=True
        )
        db_session.add_all([future_seat, past_seat])
        db_session.commit()
        db_session.refresh(future_seat)
        db_session.refresh(past_seat)

        future_reservation = Reservation(
            user_id=user.id,
            showtime_id=future_showtime.id,
            seat_id=future_seat.id,
            status=ReservationStatus.CONFIRMED,
        )
        past_reservation = Reservation(
            user_id=user.id,
            showtime_id=past_showtime.id,
            seat_id=past_seat.id,
            status=ReservationStatus.CONFIRMED,
        )
        db_session.add_all([future_reservation, past_reservation])
        db_session.commit()

        all_reservations = ReservationService.get_user_reservations(db_session, user.id)
        assert len(all_reservations) == 2

        upcoming_reservations = ReservationService.get_user_reservations(
            db_session, user.id, upcoming_only=True
        )
        assert len(upcoming_reservations) == 1
        assert upcoming_reservations[0].id == future_reservation.id
