from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Seat(Base):
    __tablename__ = "seats"
    
    id = Column(Integer, primary_key=True, index=True)
    showtime_id = Column(Integer, ForeignKey("showtimes.id"), nullable=False)
    row = Column(String(5), nullable=False)
    number = Column(Integer, nullable=False)
    is_reserved = Column(Boolean, default=False)
    
    showtime = relationship("Showtime", back_populates="seats")
    reservation = relationship("Reservation", back_populates="seat", uselist=False)
    
    __table_args__ = (
        UniqueConstraint('showtime_id', 'row', 'number', name='unique_seat_per_showtime'),
    )