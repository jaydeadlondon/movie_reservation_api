from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class Showtime(Base):
    __tablename__ = "showtimes"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    hall_number = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    total_seats = Column(Integer, default=100)

    movie = relationship("Movie", back_populates="showtimes")
    seats = relationship(
        "Seat", back_populates="showtime", cascade="all, delete-orphan"
    )
    reservations = relationship("Reservation", back_populates="showtime")
