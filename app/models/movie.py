from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    poster_url = Column(String)
    genre = Column(String, index=True)
    duration_minutes = Column(Integer)

    showtimes = relationship(
        "Showtime", back_populates="movie", cascade="all, delete-orphan"
    )
