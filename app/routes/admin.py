from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from app.database import get_db
from app.models.reservation import Reservation, ReservationStatus
from app.models.showtime import Showtime
from app.models.user import User, UserRole
from app.models.movie import Movie
from app.dependencies import require_admin
from fastapi import HTTPException

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/report/reservations")
def get_reservations_report(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    query = (
        db.query(
            Showtime.id.label("showtime_id"),
            Movie.title.label("movie_title"),
            Showtime.start_time,
            Showtime.hall_number,
            Showtime.total_seats,
            func.count(Reservation.id).label("reserved_seats"),
            (Showtime.price * func.count(Reservation.id)).label("revenue"),
        )
        .join(Reservation, Showtime.id == Reservation.showtime_id)
        .join(Movie, Showtime.movie_id == Movie.id)
        .filter(Reservation.status == ReservationStatus.CONFIRMED)
    )

    if start_date:
        query = query.filter(
            Showtime.start_time >= datetime.combine(start_date, datetime.min.time())
        )
    if end_date:
        query = query.filter(
            Showtime.start_time <= datetime.combine(end_date, datetime.max.time())
        )

    query = query.group_by(
        Showtime.id,
        Movie.title,
        Showtime.start_time,
        Showtime.hall_number,
        Showtime.total_seats,
        Showtime.price,
    )

    results = query.all()

    report = []
    total_revenue = 0

    for r in results:
        capacity_percentage = (
            (r.reserved_seats / r.total_seats * 100) if r.total_seats > 0 else 0
        )
        total_revenue += float(r.revenue)

        report.append(
            {
                "showtime_id": r.showtime_id,
                "movie_title": r.movie_title,
                "start_time": r.start_time,
                "hall_number": r.hall_number,
                "total_seats": r.total_seats,
                "reserved_seats": r.reserved_seats,
                "capacity_percentage": round(capacity_percentage, 2),
                "revenue": float(r.revenue),
            }
        )

    return {
        "report": report,
        "total_revenue": total_revenue,
        "total_showtimes": len(report),
    }


@router.post("/users/{user_id}/promote")
def promote_user_to_admin(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = UserRole.ADMIN
    db.commit()

    return {"message": f"User {user.username} promoted to admin"}
