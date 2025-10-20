from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.movie import Movie
from app.models.showtime import Showtime
from app.models.seat import Seat
from datetime import datetime, date
from typing import List

class MovieService:
    
    @staticmethod
    def create_showtime_with_seats(
        db: Session,
        movie_id: int,
        start_time: datetime,
        hall_number: int,
        price: float,
        total_seats: int = 100
    ) -> Showtime:
        
        showtime = Showtime(
            movie_id=movie_id,
            start_time=start_time,
            hall_number=hall_number,
            price=price,
            total_seats=total_seats
        )
        db.add(showtime)
        db.flush()
        
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        seats_per_row = 10
        
        for row in rows:
            for number in range(1, seats_per_row + 1):
                seat = Seat(
                    showtime_id=showtime.id,
                    row=row,
                    number=number,
                    is_reserved=False
                )
                db.add(seat)
        
        db.commit()
        db.refresh(showtime)
        
        return showtime
    
    @staticmethod
    def get_movies_with_showtimes(db: Session, target_date: date) -> List[dict]:
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        movies = db.query(Movie).join(Showtime).filter(
            Showtime.start_time.between(start_of_day, end_of_day)
        ).distinct().all()
        
        result = []
        for movie in movies:
            showtimes = db.query(Showtime).filter(
                Showtime.movie_id == movie.id,
                Showtime.start_time.between(start_of_day, end_of_day)
            ).all()
            
            showtimes_data = []
            for showtime in showtimes:
                available_seats = db.query(Seat).filter(
                    Seat.showtime_id == showtime.id,
                    Seat.is_reserved == False
                ).count()
                
                showtimes_data.append({
                    "id": showtime.id,
                    "start_time": showtime.start_time,
                    "hall_number": showtime.hall_number,
                    "price": float(showtime.price),
                    "available_seats": available_seats,
                    "total_seats": showtime.total_seats
                })
            
            result.append({
                "movie": movie,
                "showtimes": showtimes_data
            })
        
        return result
    
    @staticmethod
    def get_available_seats(db: Session, showtime_id: int) -> List[Seat]:
        return db.query(Seat).filter(
            Seat.showtime_id == showtime_id,
            Seat.is_reserved == False
        ).all()