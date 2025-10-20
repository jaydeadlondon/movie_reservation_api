from pydantic import BaseModel
from datetime import datetime
from typing import List

class SeatInfo(BaseModel):
    id: int
    row: str
    number: int
    is_reserved: bool
    
    class Config:
        from_attributes = True

class ReservationCreate(BaseModel):
    showtime_id: int
    seat_ids: List[int]

class ReservationResponse(BaseModel):
    id: int
    showtime_id: int
    seat_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReservationDetail(BaseModel):
    id: int
    movie_title: str
    showtime: datetime
    hall_number: int
    seat_row: str
    seat_number: int
    status: str
    created_at: datetime