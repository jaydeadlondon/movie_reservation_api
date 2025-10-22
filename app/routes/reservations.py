from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationDetail,
)
from app.dependencies import get_current_user
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post(
    "/", response_model=List[ReservationResponse], status_code=status.HTTP_201_CREATED
)
def create_reservation(
    reservation_data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservations = ReservationService.reserve_seats(
        db=db,
        user_id=current_user.id,
        showtime_id=reservation_data.showtime_id,
        seat_ids=reservation_data.seat_ids,
    )
    return reservations


@router.get("/my")
def get_my_reservations(
    upcoming_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservations = ReservationService.get_user_reservations(
        db, current_user.id, upcoming_only
    )

    result = []
    for res in reservations:
        result.append(
            {
                "id": res.id,
                "movie_title": res.showtime.movie.title,
                "showtime": res.showtime.start_time,
                "hall_number": res.showtime.hall_number,
                "seat_row": res.seat.row,
                "seat_number": res.seat.number,
                "status": res.status.value,
                "created_at": res.created_at,
            }
        )

    return result


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ReservationService.cancel_reservation(db, reservation_id, current_user.id)
    return None
