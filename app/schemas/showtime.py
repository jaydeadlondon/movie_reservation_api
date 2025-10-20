from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from app.schemas.movie import MovieResponse

class ShowtimeCreate(BaseModel):
    movie_id: int
    start_time: datetime
    hall_number: int
    price: Decimal
    total_seats: int = 100

class ShowtimeResponse(BaseModel):
    id: int
    movie_id: int
    start_time: datetime
    hall_number: int
    price: Decimal
    total_seats: int
    available_seats: int
    movie: MovieResponse
    
    class Config:
        from_attributes = True