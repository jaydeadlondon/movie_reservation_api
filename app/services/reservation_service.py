from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models.reservation import Reservation, ReservationStatus
from app.models.seat import Seat
from app.models.showtime import Showtime
from typing import List
from datetime import datetime

class ReservationService:
    
    @staticmethod
    def reserve_seats(
        db: Session,
        user_id: int,
        showtime_id: int,
        seat_ids: List[int]
    ) -> List[Reservation]:
        
        showtime = db.query(Showtime).filter(Showtime.id == showtime_id).first()
        if not showtime:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime not found"
            )
        
        if showtime.start_time < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reserve seats for past showtimes"
            )
        
        seats = db.query(Seat).filter(
            and_(
                Seat.id.in_(seat_ids),
                Seat.showtime_id == showtime_id
            )
        ).with_for_update().all()
        
        if len(seats) != len(seat_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some seats not found"
            )
        
        reserved_seats = [seat for seat in seats if seat.is_reserved]
        if reserved_seats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Seats already reserved: {[f'{s.row}{s.number}' for s in reserved_seats]}"
            )
        
        reservations = []
        for seat in seats:
            seat.is_reserved = True
            
            reservation = Reservation(
                user_id=user_id,
                showtime_id=showtime_id,
                seat_id=seat.id,
                status=ReservationStatus.CONFIRMED
            )
            db.add(reservation)
            reservations.append(reservation)
        
        db.commit()
        
        for reservation in reservations:
            db.refresh(reservation)
        
        return reservations
    
    @staticmethod
    def cancel_reservation(
        db: Session,
        reservation_id: int,
        user_id: int
    ) -> Reservation:
        reservation = db.query(Reservation).filter(
            Reservation.id == reservation_id
        ).first()
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found"
            )
        
        if reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your reservation"
            )
        
        if reservation.showtime.start_time < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel past reservations"
            )
        
        if reservation.status == ReservationStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservation already cancelled"
            )
        
        reservation.status = ReservationStatus.CANCELLED
        
        seat = db.query(Seat).filter(Seat.id == reservation.seat_id).first()
        seat.is_reserved = False
        
        db.commit()
        db.refresh(reservation)
        
        return reservation
    
    @staticmethod
    def get_user_reservations(db: Session, user_id: int, upcoming_only: bool = False):
        query = db.query(Reservation).filter(
            Reservation.user_id == user_id,
            Reservation.status == ReservationStatus.CONFIRMED
        )
        
        if upcoming_only:
            query = query.join(Showtime).filter(
                Showtime.start_time > datetime.utcnow()
            )
        
        return query.all()