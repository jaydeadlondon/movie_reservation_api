from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.showtime import Showtime
from app.schemas.showtime import ShowtimeCreate
from app.schemas.reservation import SeatInfo
from app.dependencies import require_admin
from app.services.movie_service import MovieService
from app.models.user import User

router = APIRouter(prefix="/showtimes", tags=["Showtimes"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_showtime(
    showtime_data: ShowtimeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    showtime = MovieService.create_showtime_with_seats(
        db=db,
        movie_id=showtime_data.movie_id,
        start_time=showtime_data.start_time,
        hall_number=showtime_data.hall_number,
        price=float(showtime_data.price),
        total_seats=showtime_data.total_seats,
    )
    return {"id": showtime.id, "message": "Showtime created with seats"}


@router.get("/{showtime_id}/seats", response_model=List[SeatInfo])
def get_showtime_seats(showtime_id: int, db: Session = Depends(get_db)):
    showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
    if not showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")

    return showtime.seats


@router.get("/{showtime_id}/available-seats", response_model=List[SeatInfo])
def get_available_seats(showtime_id: int, db: Session = Depends(get_db)):
    return MovieService.get_available_seats(db, showtime_id)
