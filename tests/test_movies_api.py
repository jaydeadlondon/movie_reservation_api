from fastapi import status
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.models.showtime import Showtime
from app.utils import get_password_hash, create_access_token


class TestMoviesAPI:
    """Тесты для API фильмов"""

    def test_get_movies_empty(self, client):
        """Тест получения списка фильмов (пустой)"""
        response = client.get("/movies/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_movies_with_data(self, client, db_session, test_movie_data):
        """Тест получения списка фильмов с данными"""
        movie = Movie(**test_movie_data)
        db_session.add(movie)
        db_session.commit()

        response = client.get("/movies/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == test_movie_data["title"]
        assert data[0]["genre"] == test_movie_data["genre"]

    def test_get_movie_by_id(self, client, db_session, test_movie_data):
        """Тест получения фильма по ID"""
        movie = Movie(**test_movie_data)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        response = client.get(f"/movies/{movie.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == movie.id
        assert data["title"] == test_movie_data["title"]

    def test_get_movie_not_found(self, client):
        """Тест получения несуществующего фильма"""
        response = client.get("/movies/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Movie not found" in response.json()["detail"]

    def test_create_movie_unauthorized(self, client, test_movie_data):
        """Тест создания фильма без авторизации"""
        response = client.post("/movies/", json=test_movie_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_movie_as_user(self, client, test_movie_data, db_session):
        """Тест создания фильма обычным пользователем"""
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

        response = client.post("/movies/", json=test_movie_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in response.json()["detail"]

    def test_create_movie_as_admin(self, client, test_movie_data, db_session):
        """Тест создания фильма администратором"""
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

        response = client.post("/movies/", json=test_movie_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == test_movie_data["title"]
        assert data["genre"] == test_movie_data["genre"]
        assert "id" in data

    def test_update_movie_as_admin(self, client, test_movie_data, db_session):
        """Тест обновления фильма администратором"""
        movie = Movie(**test_movie_data)
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

        update_data = {"title": "Updated Movie Title", "genre": "Comedy"}
        response = client.put(f"/movies/{movie.id}", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Movie Title"
        assert data["genre"] == "Comedy"
        assert data["id"] == movie.id

    def test_delete_movie_as_admin(self, client, test_movie_data, db_session):
        """Тест удаления фильма администратором"""
        movie = Movie(**test_movie_data)
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

        response = client.delete(f"/movies/{movie.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = client.get(f"/movies/{movie.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_movies_schedule(self, client, db_session, test_movie_data):
        """Тест получения расписания фильмов"""
        movie = Movie(**test_movie_data)
        db_session.add(movie)
        db_session.commit()
        db_session.refresh(movie)

        tomorrow = datetime.utcnow() + timedelta(days=1)
        showtime = Showtime(
            movie_id=movie.id,
            start_time=tomorrow,
            hall_number=1,
            price=Decimal("15.50"),
            total_seats=100,
        )
        db_session.add(showtime)
        db_session.commit()

        response = client.get("/movies/schedule")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["movie"]["title"] == test_movie_data["title"]
        assert len(data[0]["showtimes"]) == 1
        assert data[0]["showtimes"][0]["hall_number"] == 1
